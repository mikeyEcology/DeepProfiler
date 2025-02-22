import pandas as pd

import deepprofiler.dataset.utils


def parse_delimiter(delimiter):
    if delimiter == "blanks":
        return "\s+"
    elif delimiter == "tabs":
        return "\t"
    else:
        return ","

#TODO: This function is only useful for the LUAD dataset
def conditionalWellName(row):
    if row["Metadata_Plate"] in ["52650", "52661"]:
        return row["Metadata_Well"]
    else:
        return row["Metadata_Well"].upper()

## Generator of plates. Reads metadata and yields plates
def read_plates(metaFile):
    metadata = Metadata(metaFile)
    plates = metadata.data["Metadata_Plate"].unique()
    deepprofiler.dataset.utils.logger.info("Total plates: {}".format(len(plates)))
    for i in range(len(plates)):  #  & (df.Metadata_Well == "a01")
        plate = metadata.filterRecords(lambda df: (df.Metadata_Plate == plates[i]), copy=True)
        yield plate
    return

class Metadata():

    # The dtype argument indicates whether the dataset should be read as strings (object)
    # or according to the dataset type (None)
    def __init__(self, filename=None, csvMode="single", delimiter="default", dtype=object):
        if filename is not None:
            if csvMode == "single":
                self.loadSingle(filename, delimiter, dtype)
            elif csvMode == "multi":
                self.loadMultiple(filename, delimiter, dtype)

    def loadSingle(self, filename, delim, dtype):
        print("Reading metadata form", filename)
        delimiter = parse_delimiter(delim)
        # Read csv files as strings without dropping NA symbols
        self.data = pd.read_csv(filename, delimiter=delimiter, dtype=dtype, keep_default_na=False)

    def loadMultiple(self, filename, delim, dtype):
        frames = []
        delimiter = parse_delimiter(delim)
        with open(filename, "r") as filelist:
            for line in filelist:
                csvPath = line.replace("\n","")
                print("Reading from", csvPath)
                frames.append( pd.read_csv(csvPath, delimiter=delimiter, dtype=dtype, keep_default_na=False) )
        self.data = pd.concat(frames)
        print("Multiple CSV files loaded")

    def filterRecords(self, filteringRule, copy=False):
        if copy:
            newMeta = Metadata()
            newMeta.data = self.data.loc[filteringRule(self.data), :].copy()
            return newMeta
        else:
            self.data = self.data.loc[filteringRule(self.data), :]

    def splitMetadata(self, trainingRule, validationRule):
        self.train = self.data[trainingRule(self.data)].copy()
        self.val = self.data[validationRule(self.data)].copy()

    def mergeOutlines(self, outlines_df):
        result = pd.merge(self.data, outlines_df, on=["Metadata_Plate", "Metadata_Well", "Metadata_Site"])
        print("Metadata merged with Outlines")
        self.data = result
