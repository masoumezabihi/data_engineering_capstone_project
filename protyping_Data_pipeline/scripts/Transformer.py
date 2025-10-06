import pandas as pd
import json
from Logger import Logger

class Transformer:
    def __init__(self, records):
        """
        Transformer initialized with extracted JSON records.
        """
        self.records = records
        Logger.log("Transformer initialized with records.")

    def extract_report_table(self):
        Logger.log("Extracting report table...")
        df = pd.json_normalize(self.records, sep=".")
        # Drop nested patient fields
        df = df.drop(columns=[col for col in df.columns if col.startswith("patient.")], errors="ignore")
        Logger.log(f"Report table extracted with {len(df)} rows.")
        return df

    def extract_patient_table(self):
        Logger.log("Extracting patient table...")
        patients = []
        for r in self.records:
            patient = r.get("patient", {})
            patients.append({
                "safetyreportid": r.get("safetyreportid"),
                "onset_age": patient.get("patientonsetage"),
                "onset_age_unit": patient.get("patientonsetageunit"),
                "weight": patient.get("patientweight"),
                "sex": patient.get("patientsex"),
                "age_group": patient.get("patientagegroup"),
                "narrative": patient.get("summary", {}).get("narrativeincludeclinical"),
                "death_date": patient.get("patientdeath", {}).get("patientdeathdate"),
                "death_date_format": patient.get("patientdeath", {}).get("patientdeathdateformat")
            })
        df = pd.DataFrame(patients)
        Logger.log(f"Patient table extracted with {len(df)} rows.")
        return df

    def extract_drug_table(self):
        Logger.log("Extracting drug table...")
        df = pd.json_normalize(
            self.records,
            record_path=["patient", "drug"],
            meta=["safetyreportid"],
            sep="."
        )
        # Combine openfda fields into one JSON column
        openfda_cols = [c for c in df.columns if c.startswith("openfda")]
        df["openfda"] = df[openfda_cols].apply(lambda row: row.dropna().to_dict(), axis=1)
        df = df.drop(columns=openfda_cols, errors="ignore")
        Logger.log(f"Drug table extracted with {len(df)} rows.")
        return df

    def extract_reaction_table(self):
        Logger.log("Extracting reaction table...")
        df = pd.json_normalize(
            self.records,
            record_path=["patient", "reaction"],
            meta=["safetyreportid"],
            sep="."
        )
        Logger.log(f"Reaction table extracted with {len(df)} rows.")
        return df

    def drop_columns(self, df, cols):
        Logger.log(f"Dropping columns: {cols}")
        return df.drop(columns=cols, errors="ignore")

    def convert_dates(self, df, cols):
        for c in cols:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="coerce")
        return df

    def add_category_label(self, df, column, new_column, value_map, default="Unknown"):
        if column not in df.columns:
            return df
        df[new_column] = df[column].map(value_map).fillna(default)
        return df

    def show_missing_percentage(self, df):
        return df.isnull().mean().reset_index().rename(columns={"index": "column_name", 0: "percent_missing"})

    def drop_high_missing(self, df, threshold=0.95):
        missing = self.show_missing_percentage(df)
        high_missing_cols = missing[missing["percent_missing"] > threshold].column_name.tolist()
        return self.drop_columns(df, high_missing_cols)
 