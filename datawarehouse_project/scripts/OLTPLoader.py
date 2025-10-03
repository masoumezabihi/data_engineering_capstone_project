import os
import pandas as pd


class OLTPLoader:
    def __init__ (self, raw_data_folder, table_columns):
        self.raw_data_folder = raw_data_folder
        self.table_columns = table_columns
        self.data_frames = {}

    def load_all_tables(self):
        for file_name, columns in self.table_columns.items():
            file_path = os.path.join(self.raw_data_folder, file_name)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, sep="|", header=None, names=columns, index_col= False)
                self.data_frames[file_name] = df
            else:
                print(f"Warning: {file_name} not found in {self.raw_data_folder}")

        return self.data_frames
    
    def describe_tables(self):
        for table_name, df in self.data_frames.items():
            print("=============table name=============")
            print(table_name)
            print("=============shape=============")
            print(df.shape)
            print("=============describe=============")
            print(df.describe())
            print("=============info=============")
            print(df.info())
            print("============missing value per column==============")
            print(df.isnull().sum())
            print("*********************************************")