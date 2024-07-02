import pydicom
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
import datetime

# output filename
output_filename = "output3.dcm"

# Create the File Meta Information
file_meta = pydicom.dataset.Dataset()
# FileMetaInformationGroupLength only gets rewritten when saved if present
file_meta.FileMetaInformationGroupLength = 206

file_meta.MediaStorageSOPClassUID = pydicom.uid.UID('1.2.840.10008.5.1.4.1.1.88.11')  # Basic Text SR
file_meta.MediaStorageSOPInstanceUID = generate_uid()
file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
file_meta.ImplementationClassUID = generate_uid()

# IMPORTANT to enforce standard!
# see: https://pydicom.github.io/pydicom/dev/reference/generated/pydicom.dataset.validate_file_meta.html
pydicom.dataset.validate_file_meta(file_meta, enforce_standard=True)

# see: http://dicom.nema.org/dicom/2013/output/chtml/part10/chapter_7.html
preamble = b"\0" * 128

# Create the main FileDataset instance (initially no data elements, but file_meta supplied)
ds = pydicom.dataset.FileDataset(output_filename, {}, file_meta=file_meta, preamble=preamble)

# Set the required DICOM metadata
ds.PatientName = "LUNITIAN^TEST"
ds.PatientID = "123456"
ds.StudyInstanceUID = generate_uid()
ds.SeriesInstanceUID = generate_uid()
ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
ds.Modality = "SR"
ds.StudyDate = "20240101"
ds.StudyTime = "120000"
ds.AccessionNumber = "12345678"
ds.SeriesNumber = "1"
ds.InstanceNumber = "1"
ds.ContentDate = "20240101"
ds.ContentTime = "120000"

# Set the transfer syntax
ds.is_little_endian = True
ds.is_implicit_VR = False

ds.SpecificCharacterSet = 'ISO_IR 192' # Unicode in UTF-8

dt = datetime.datetime.now()
ds.InstanceCreationDate = dt.strftime('%Y%m%d')
ds.InstanceCreationTime = dt.strftime('%H%M%S')  # ('%H%M%S.%f')

# Create the root content sequence
ds.ContentSequence = []

# Create the root container for the General Purpose Report (TID 4000)
root_container = Dataset()
root_container.RelationshipType = "CONTAINS"
root_container.ValueType = "CONTAINER"
root_container.ConceptNameCodeSequence = [Dataset()]
root_container.ConceptNameCodeSequence[0].CodeValue = "18748-4"
root_container.ConceptNameCodeSequence[0].CodingSchemeDesignator = "LN"
root_container.ConceptNameCodeSequence[0].CodeMeaning = "General Purpose Report"
root_container.ContinuityOfContent = "SEPARATE"
root_container.ContentSequence = []

# Add TID 4000 identifier
tid_4000_identifier = Dataset()
tid_4000_identifier.RelationshipType = "HAS CONCEPT MOD"
tid_4000_identifier.ValueType = "CODE"
tid_4000_identifier.ConceptNameCodeSequence = [Dataset()]
tid_4000_identifier.ConceptNameCodeSequence[0].CodeValue = "111036"
tid_4000_identifier.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
tid_4000_identifier.ConceptNameCodeSequence[0].CodeMeaning = "Document Title"
tid_4000_identifier.ConceptCodeSequence = [Dataset()]
tid_4000_identifier.ConceptCodeSequence[0].CodeValue = "T-4000"
tid_4000_identifier.ConceptCodeSequence[0].CodingSchemeDesignator = "TID"
tid_4000_identifier.ConceptCodeSequence[0].CodeMeaning = "TID 4000"

# Append TID 4000 identifier to the root container
root_container.ContentSequence.append(tid_4000_identifier)

# Create the Imaging Report Content container (TID 4002)
report_content_item = Dataset()
report_content_item.RelationshipType = "CONTAINS"
report_content_item.ValueType = "CONTAINER"
report_content_item.ConceptNameCodeSequence = [Dataset()]
report_content_item.ConceptNameCodeSequence[0].CodeValue = "18748-4"
report_content_item.ConceptNameCodeSequence[0].CodingSchemeDesignator = "LN"
report_content_item.ConceptNameCodeSequence[0].CodeMeaning = "Imaging Report Content"
report_content_item.ContinuityOfContent = "SEPARATE"
report_content_item.ContentSequence = []

# Create a text content item for arbitrary text within Imaging Report Content
text_content_item = Dataset()
text_content_item.RelationshipType = "CONTAINS"
text_content_item.ValueType = "TEXT"
text_content_item.ConceptNameCodeSequence = [Dataset()]
text_content_item.ConceptNameCodeSequence[0].CodeValue = "121106"
text_content_item.ConceptNameCodeSequence[0].CodingSchemeDesignator = "DCM"
text_content_item.ConceptNameCodeSequence[0].CodeMeaning = "Finding"
text_content_item.TextValue = "This is an arbitrary short text."

# Append the text content item to the report content container
report_content_item.ContentSequence.append(text_content_item)

# Append the report content container to the root container
root_container.ContentSequence.append(report_content_item)

# Append the root container to the root content sequence
ds.ContentSequence.append(root_container)

# Add Referenced SOP Instance UID
ref_sop_instance_uid = Dataset()
ref_sop_instance_uid.ReferencedSOPInstanceUID = ds.SOPInstanceUID

# Save the dataset to a DICOM file
ds.save_as(output_filename)

print(f"DICOM SR document created and saved as '{output_filename}'")
