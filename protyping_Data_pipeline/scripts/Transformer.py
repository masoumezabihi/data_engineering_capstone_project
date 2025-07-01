import pandas as pd
import json
from Logger import Logger  

class Transformer:
    def __init__(self, records):
        """
        Initialize the Transformer with records.
        
        Parameters:
            records (list): The list of JSON records to process.
        """
        self.records = records
        Logger.log("Transformer initialized with records.")

    def flatten_json_table(self, data, record_path=None, meta=None, record_prefix="", meta_prefix="", sep="."):
        """
        Generic flattening using pandas.json_normalize.
        
        Parameters:
            data (list): The data to normalize.
            record_path (list or None): The path to the records to normalize.
            meta (list or None): The metadata fields to include.
            record_prefix (str): Prefix to add to the flattened record fields.
            meta_prefix (str): Prefix to add to the metadata fields.
            sep (str): Separator to use between levels of the flattened column names.

        Returns:
            DataFrame: A pandas DataFrame with flattened data.
        """
        try:
            Logger.log(f"Flattening JSON with record_path={record_path} and meta={meta}")
            return pd.json_normalize(
                data=data,
                record_path=record_path,
                meta=meta,
                record_prefix=record_prefix,
                meta_prefix=meta_prefix,
                sep=sep
            )
        except Exception as e:
            Logger.log(f"Error during flattening: {e}")
            raise e

    def extract_report_table(self):
        """
        Extract report data into a normalized table.
        
        Returns:
            DataFrame: A pandas DataFrame with the normalized report data.
        """
        try:
            Logger.log("Extracting report table.")
            report_df = self.flatten_json_table(data=self.records, sep=".")
            report_df.drop(columns=[col for col in report_df.columns if col.startswith("patient.")], inplace=True)
            report_df = self.drop_constant_columns(report_df)  # Call the drop_constant_columns method from the class
            Logger.log(f"Report table extracted with {len(report_df)} rows.")
            return report_df
        except Exception as e:
            Logger.log(f"Error extracting report table: {e}")
            raise e

    def extract_patient_table(self):
        """
        Extract patient data into a normalized table.
        
        Returns:
            DataFrame: A pandas DataFrame with the normalized patient data.
        """
        try:
            Logger.log("Extracting patient table.")
            patients = []
            for record in self.records:
                safetyreportid = record.get("safetyreportid")
                patient = record.get("patient", {})
                summary = patient.get("summary", {})
                patientdeath = patient.get("patientdeath", {})
                patients.append({
                    "safetyreportid": safetyreportid,
                    "patientonsetage": patient.get("patientonsetage"),
                    "patientonsetageunit": patient.get("patientonsetageunit"),
                    "patientweight": patient.get("patientweight"),
                    "patientsex": patient.get("patientsex"),
                    "patientagegroup": patient.get("patientagegroup"),
                    "summary": summary.get("narrativeincludeclinical"),
                    "patientdeathdateformat": patientdeath.get("patientdeathdateformat"),
                    "patientdeathdate": patientdeath.get("patientdeathdate")
                })
            Logger.log(f"Patient table extracted with {len(patients)} records.")
            return pd.DataFrame(patients)
        except Exception as e:
            Logger.log(f"Error extracting patient table: {e}")
            raise e

    def extract_drug_table(self):
        """
        Extract drug data, merge openfda fields into one jsonb column.
        
        Returns:
            DataFrame: A pandas DataFrame with the normalized drug data.
        """
        try:
            Logger.log("Extracting drug table.")
            df_drug = self.flatten_json_table(
                data=self.records,
                record_path=["patient", "drug"],
                meta=["safetyreportid"],
                record_prefix="drug.",
                meta_prefix="report.",
                sep="."
            )

            # Identify all openfda.* columns
            openfda_cols = [col for col in df_drug.columns if col.startswith("drug.openfda.")]

            def combine_openfda(row):
                openfda_data = {col.replace("drug.openfda.", ""): row[col] for col in openfda_cols}
                return json.dumps(openfda_data)
          
            # Create a single openfda json column
            df_drug["openfda"] = df_drug.apply(combine_openfda, axis=1)

            # Drop the original openfda.* columns
            df_drug.drop(columns=openfda_cols, inplace=True)

            # Clean up column names
            df_drug.columns = [col.replace("drug.", "").replace("report.", "") for col in df_drug.columns]
            Logger.log(f"Drug table extracted with {len(df_drug)} rows.")
            return df_drug
        except Exception as e:
            Logger.log(f"Error extracting drug table: {e}")
            raise e

    def extract_reaction_table(self):
        """
        Extract reaction data from nested JSON.
        
        Returns:
            DataFrame: A pandas DataFrame with the normalized reaction data.
        """
        try:
            Logger.log("Extracting reaction table.")
            df_reaction = self.flatten_json_table(
                data=self.records,
                record_path=["patient", "reaction"],
                meta=["safetyreportid"],
                record_prefix="reaction.",
                meta_prefix="report.",
                sep="."
            )
            df_reaction.columns = [col.split('.')[-1] for col in df_reaction.columns]
            Logger.log(f"Reaction table extracted with {len(df_reaction)} rows.")
            return df_reaction
        except Exception as e:
            Logger.log(f"Error extracting reaction table: {e}")
            raise e

    def find_homogeneous_columns(self, df):
        """
        Identify columns in a DataFrame that contain only a single unique (non-list) value.
        Ignores columns that contain list-type values.
        
        Parameters:
            df (pd.DataFrame): The input DataFrame

        Returns:
            List[str]: Column names with a single unique value
        """
        try:
            Logger.log("Identifying homogeneous columns.")
            homogeneous_cols = []

            for col in df.columns:
                # Skip columns that contain any lists
                if df[col].apply(lambda x: isinstance(x, list)).any():
                    continue
                # Check if column has only one unique value (including NaN)
                if df[col].nunique(dropna=False) == 1:
                    homogeneous_cols.append(col)

            Logger.log(f"Found {len(homogeneous_cols)} homogeneous columns.")
            return homogeneous_cols
        except Exception as e:
            Logger.log(f"Error finding homogeneous columns: {e}")
            raise e

    def show_missing_percentage(self, df):
        """
        Show the percentage of missing values in each column.
        
        Parameters:
            df (pd.DataFrame): The input DataFrame
        
        Returns:
            DataFrame: A pandas DataFrame with columns and their missing percentages
        """
        try:
            Logger.log("Calculating missing values percentage.")
            percent_missing = df.isnull().sum() * 100 / len(df)

            missing_value_df = pd.DataFrame({
                'column_name': df.columns,
                'percent_missing': percent_missing.values
            })

            missing_value_df.sort_values('percent_missing', ascending=False, inplace=True)
            return missing_value_df
        except Exception as e:
            Logger.log(f"Error calculating missing percentage: {e}")
            raise e

    def check_column_homogeneity(self, df):
        """
        Checks whether each column in the DataFrame contains only one data type (excluding NaNs).

        Returns:
            dict: A dictionary with column names as keys and type counts as values for non-homogeneous columns.
        """
        try:
            Logger.log("Checking column homogeneity.")
            non_homogeneous_columns = {}

            for column in df.columns:
                non_null_series = df[column].dropna()

                if non_null_series.empty:
                    continue

                type_counts = non_null_series.map(type).value_counts()

                if len(type_counts) > 1:
                    non_homogeneous_columns[column] = type_counts

            Logger.log(f"Found {len(non_homogeneous_columns)} non-homogeneous columns.")
            return non_homogeneous_columns
        except Exception as e:
            Logger.log(f"Error checking column homogeneity: {e}")
            raise e

    def drop_constant_columns(self, df):
        """
        Drops columns with constant values from a Pandas DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame.

        Returns:
            pd.DataFrame: The DataFrame with constant columns removed.
        """
        try:
            Logger.log("Dropping constant columns.")
            constant_columns = [col for col in df.columns if len(df[col].unique()) == 1]
            df.drop(constant_columns, axis=1, inplace=True)
            Logger.log(f"Dropped {len(constant_columns)} constant columns.")
            return df
        except Exception as e:
            Logger.log(f"Error dropping constant columns: {e}")
            raise e
