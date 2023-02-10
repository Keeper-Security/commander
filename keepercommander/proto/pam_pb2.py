# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pam.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import enterprise_pb2 as enterprise__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tpam.proto\x12\x03PAM\x1a\x10\x65nterprise.proto\"\x83\x01\n\x13PAMRotationSchedule\x12\x11\n\trecordUid\x18\x01 \x01(\x0c\x12\x18\n\x10\x63onfigurationUid\x18\x02 \x01(\x0c\x12\x15\n\rcontrollerUid\x18\x03 \x01(\x0c\x12\x14\n\x0cscheduleData\x18\x04 \x01(\t\x12\x12\n\nnoSchedule\x18\x05 \x01(\x08\"K\n\x1cPAMRotationSchedulesResponse\x12+\n\tschedules\x18\x01 \x03(\x0b\x32\x18.PAM.PAMRotationSchedule\"+\n\x14PAMOnlineControllers\x12\x13\n\x0b\x63ontrollers\x18\x01 \x03(\x0c\"9\n\x10PAMRotateRequest\x12\x12\n\nrequestUid\x18\x01 \x01(\x0c\x12\x11\n\trecordUid\x18\x02 \x01(\x0c\"A\n\x16PAMControllersResponse\x12\'\n\x0b\x63ontrollers\x18\x01 \x03(\x0b\x32\x12.PAM.PAMController\"=\n\x13PAMRemoveController\x12\x15\n\rcontrollerUid\x18\x01 \x01(\x0c\x12\x0f\n\x07message\x18\x02 \x01(\t\"L\n\x1bPAMRemoveControllerResponse\x12-\n\x0b\x63ontrollers\x18\x01 \x03(\x0b\x32\x18.PAM.PAMRemoveController\"=\n\x10PAMModifyRequest\x12)\n\noperations\x18\x01 \x03(\x0b\x32\x15.PAM.PAMDataOperation\"\x98\x01\n\x10PAMDataOperation\x12,\n\roperationType\x18\x01 \x01(\x0e\x32\x15.PAM.PAMOperationType\x12\x30\n\rconfiguration\x18\x02 \x01(\x0b\x32\x19.PAM.PAMConfigurationData\x12$\n\x07\x65lement\x18\x03 \x01(\x0b\x32\x13.PAM.PAMElementData\"e\n\x14PAMConfigurationData\x12\x18\n\x10\x63onfigurationUid\x18\x01 \x01(\x0c\x12\x0e\n\x06nodeId\x18\x02 \x01(\x03\x12\x15\n\rcontrollerUid\x18\x03 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x04 \x01(\x0c\"E\n\x0ePAMElementData\x12\x12\n\nelementUid\x18\x01 \x01(\x0c\x12\x11\n\tparentUid\x18\x02 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\"m\n\x19PAMElementOperationResult\x12\x12\n\nelementUid\x18\x01 \x01(\x0c\x12+\n\x06result\x18\x02 \x01(\x0e\x32\x1b.PAM.PAMOperationResultType\x12\x0f\n\x07message\x18\x03 \x01(\t\"B\n\x0fPAMModifyResult\x12/\n\x07results\x18\x01 \x03(\x0b\x32\x1e.PAM.PAMElementOperationResult\"x\n\nPAMElement\x12\x12\n\nelementUid\x18\x01 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x12\x0f\n\x07\x63reated\x18\x03 \x01(\x03\x12\x14\n\x0clastModified\x18\x04 \x01(\x03\x12!\n\x08\x63hildren\x18\x05 \x03(\x0b\x32\x0f.PAM.PAMElement\"#\n\x14PAMGenericUidRequest\x12\x0b\n\x03uid\x18\x01 \x01(\x0c\"%\n\x15PAMGenericUidsRequest\x12\x0c\n\x04uids\x18\x01 \x03(\x0c\"\xab\x01\n\x10PAMConfiguration\x12\x18\n\x10\x63onfigurationUid\x18\x01 \x01(\x0c\x12\x0e\n\x06nodeId\x18\x02 \x01(\x03\x12\x15\n\rcontrollerUid\x18\x03 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x04 \x01(\x0c\x12\x0f\n\x07\x63reated\x18\x05 \x01(\x03\x12\x14\n\x0clastModified\x18\x06 \x01(\x03\x12!\n\x08\x63hildren\x18\x07 \x03(\x0b\x32\x0f.PAM.PAMElement\"B\n\x11PAMConfigurations\x12-\n\x0e\x63onfigurations\x18\x01 \x03(\x0b\x32\x15.PAM.PAMConfiguration\"\xff\x01\n\rPAMController\x12\x15\n\rcontrollerUid\x18\x01 \x01(\x0c\x12\x16\n\x0e\x63ontrollerName\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65viceToken\x18\x03 \x01(\t\x12\x12\n\ndeviceName\x18\x04 \x01(\t\x12\x0e\n\x06nodeId\x18\x05 \x01(\x03\x12\x0f\n\x07\x63reated\x18\x06 \x01(\x03\x12\x14\n\x0clastModified\x18\x07 \x01(\x03\x12\x16\n\x0e\x61pplicationUid\x18\x08 \x01(\x0c\x12\x30\n\rappClientType\x18\t \x01(\x0e\x32\x19.Enterprise.AppClientType\x12\x15\n\risInitialized\x18\n \x01(\x08\"%\n\x12\x43ontrollerResponse\x12\x0f\n\x07payload\x18\x01 \x01(\t\"M\n\x1aPAMConfigurationController\x12\x18\n\x10\x63onfigurationUid\x18\x01 \x01(\x0c\x12\x15\n\rcontrollerUid\x18\x02 \x01(\x0c\"T\n\x17\x43onfigurationAddRequest\x12\x18\n\x10\x63onfigurationUid\x18\x01 \x01(\x0c\x12\x11\n\trecordKey\x18\x02 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c*@\n\x10PAMOperationType\x12\x07\n\x03\x41\x44\x44\x10\x00\x12\n\n\x06UPDATE\x10\x01\x12\x0b\n\x07REPLACE\x10\x02\x12\n\n\x06\x44\x45LETE\x10\x03*p\n\x16PAMOperationResultType\x12\x0f\n\x0bPOT_SUCCESS\x10\x00\x12\x15\n\x11POT_UNKNOWN_ERROR\x10\x01\x12\x16\n\x12POT_ALREADY_EXISTS\x10\x02\x12\x16\n\x12POT_DOES_NOT_EXIST\x10\x03*H\n\x15\x43ontrollerMessageType\x12\x0f\n\x0b\x43MT_GENERAL\x10\x00\x12\x0e\n\nCMT_ROTATE\x10\x01\x12\x0e\n\nCMT_STREAM\x10\x02\x42\x1f\n\x18\x63om.keepersecurity.protoB\x03PAMb\x06proto3')

_PAMOPERATIONTYPE = DESCRIPTOR.enum_types_by_name['PAMOperationType']
PAMOperationType = enum_type_wrapper.EnumTypeWrapper(_PAMOPERATIONTYPE)
_PAMOPERATIONRESULTTYPE = DESCRIPTOR.enum_types_by_name['PAMOperationResultType']
PAMOperationResultType = enum_type_wrapper.EnumTypeWrapper(_PAMOPERATIONRESULTTYPE)
_CONTROLLERMESSAGETYPE = DESCRIPTOR.enum_types_by_name['ControllerMessageType']
ControllerMessageType = enum_type_wrapper.EnumTypeWrapper(_CONTROLLERMESSAGETYPE)
ADD = 0
UPDATE = 1
REPLACE = 2
DELETE = 3
POT_SUCCESS = 0
POT_UNKNOWN_ERROR = 1
POT_ALREADY_EXISTS = 2
POT_DOES_NOT_EXIST = 3
CMT_GENERAL = 0
CMT_ROTATE = 1
CMT_STREAM = 2


_PAMROTATIONSCHEDULE = DESCRIPTOR.message_types_by_name['PAMRotationSchedule']
_PAMROTATIONSCHEDULESRESPONSE = DESCRIPTOR.message_types_by_name['PAMRotationSchedulesResponse']
_PAMONLINECONTROLLERS = DESCRIPTOR.message_types_by_name['PAMOnlineControllers']
_PAMROTATEREQUEST = DESCRIPTOR.message_types_by_name['PAMRotateRequest']
_PAMCONTROLLERSRESPONSE = DESCRIPTOR.message_types_by_name['PAMControllersResponse']
_PAMREMOVECONTROLLER = DESCRIPTOR.message_types_by_name['PAMRemoveController']
_PAMREMOVECONTROLLERRESPONSE = DESCRIPTOR.message_types_by_name['PAMRemoveControllerResponse']
_PAMMODIFYREQUEST = DESCRIPTOR.message_types_by_name['PAMModifyRequest']
_PAMDATAOPERATION = DESCRIPTOR.message_types_by_name['PAMDataOperation']
_PAMCONFIGURATIONDATA = DESCRIPTOR.message_types_by_name['PAMConfigurationData']
_PAMELEMENTDATA = DESCRIPTOR.message_types_by_name['PAMElementData']
_PAMELEMENTOPERATIONRESULT = DESCRIPTOR.message_types_by_name['PAMElementOperationResult']
_PAMMODIFYRESULT = DESCRIPTOR.message_types_by_name['PAMModifyResult']
_PAMELEMENT = DESCRIPTOR.message_types_by_name['PAMElement']
_PAMGENERICUIDREQUEST = DESCRIPTOR.message_types_by_name['PAMGenericUidRequest']
_PAMGENERICUIDSREQUEST = DESCRIPTOR.message_types_by_name['PAMGenericUidsRequest']
_PAMCONFIGURATION = DESCRIPTOR.message_types_by_name['PAMConfiguration']
_PAMCONFIGURATIONS = DESCRIPTOR.message_types_by_name['PAMConfigurations']
_PAMCONTROLLER = DESCRIPTOR.message_types_by_name['PAMController']
_CONTROLLERRESPONSE = DESCRIPTOR.message_types_by_name['ControllerResponse']
_PAMCONFIGURATIONCONTROLLER = DESCRIPTOR.message_types_by_name['PAMConfigurationController']
_CONFIGURATIONADDREQUEST = DESCRIPTOR.message_types_by_name['ConfigurationAddRequest']
PAMRotationSchedule = _reflection.GeneratedProtocolMessageType('PAMRotationSchedule', (_message.Message,), {
  'DESCRIPTOR' : _PAMROTATIONSCHEDULE,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMRotationSchedule)
  })
_sym_db.RegisterMessage(PAMRotationSchedule)

PAMRotationSchedulesResponse = _reflection.GeneratedProtocolMessageType('PAMRotationSchedulesResponse', (_message.Message,), {
  'DESCRIPTOR' : _PAMROTATIONSCHEDULESRESPONSE,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMRotationSchedulesResponse)
  })
_sym_db.RegisterMessage(PAMRotationSchedulesResponse)

PAMOnlineControllers = _reflection.GeneratedProtocolMessageType('PAMOnlineControllers', (_message.Message,), {
  'DESCRIPTOR' : _PAMONLINECONTROLLERS,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMOnlineControllers)
  })
_sym_db.RegisterMessage(PAMOnlineControllers)

PAMRotateRequest = _reflection.GeneratedProtocolMessageType('PAMRotateRequest', (_message.Message,), {
  'DESCRIPTOR' : _PAMROTATEREQUEST,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMRotateRequest)
  })
_sym_db.RegisterMessage(PAMRotateRequest)

PAMControllersResponse = _reflection.GeneratedProtocolMessageType('PAMControllersResponse', (_message.Message,), {
  'DESCRIPTOR' : _PAMCONTROLLERSRESPONSE,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMControllersResponse)
  })
_sym_db.RegisterMessage(PAMControllersResponse)

PAMRemoveController = _reflection.GeneratedProtocolMessageType('PAMRemoveController', (_message.Message,), {
  'DESCRIPTOR' : _PAMREMOVECONTROLLER,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMRemoveController)
  })
_sym_db.RegisterMessage(PAMRemoveController)

PAMRemoveControllerResponse = _reflection.GeneratedProtocolMessageType('PAMRemoveControllerResponse', (_message.Message,), {
  'DESCRIPTOR' : _PAMREMOVECONTROLLERRESPONSE,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMRemoveControllerResponse)
  })
_sym_db.RegisterMessage(PAMRemoveControllerResponse)

PAMModifyRequest = _reflection.GeneratedProtocolMessageType('PAMModifyRequest', (_message.Message,), {
  'DESCRIPTOR' : _PAMMODIFYREQUEST,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMModifyRequest)
  })
_sym_db.RegisterMessage(PAMModifyRequest)

PAMDataOperation = _reflection.GeneratedProtocolMessageType('PAMDataOperation', (_message.Message,), {
  'DESCRIPTOR' : _PAMDATAOPERATION,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMDataOperation)
  })
_sym_db.RegisterMessage(PAMDataOperation)

PAMConfigurationData = _reflection.GeneratedProtocolMessageType('PAMConfigurationData', (_message.Message,), {
  'DESCRIPTOR' : _PAMCONFIGURATIONDATA,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMConfigurationData)
  })
_sym_db.RegisterMessage(PAMConfigurationData)

PAMElementData = _reflection.GeneratedProtocolMessageType('PAMElementData', (_message.Message,), {
  'DESCRIPTOR' : _PAMELEMENTDATA,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMElementData)
  })
_sym_db.RegisterMessage(PAMElementData)

PAMElementOperationResult = _reflection.GeneratedProtocolMessageType('PAMElementOperationResult', (_message.Message,), {
  'DESCRIPTOR' : _PAMELEMENTOPERATIONRESULT,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMElementOperationResult)
  })
_sym_db.RegisterMessage(PAMElementOperationResult)

PAMModifyResult = _reflection.GeneratedProtocolMessageType('PAMModifyResult', (_message.Message,), {
  'DESCRIPTOR' : _PAMMODIFYRESULT,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMModifyResult)
  })
_sym_db.RegisterMessage(PAMModifyResult)

PAMElement = _reflection.GeneratedProtocolMessageType('PAMElement', (_message.Message,), {
  'DESCRIPTOR' : _PAMELEMENT,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMElement)
  })
_sym_db.RegisterMessage(PAMElement)

PAMGenericUidRequest = _reflection.GeneratedProtocolMessageType('PAMGenericUidRequest', (_message.Message,), {
  'DESCRIPTOR' : _PAMGENERICUIDREQUEST,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMGenericUidRequest)
  })
_sym_db.RegisterMessage(PAMGenericUidRequest)

PAMGenericUidsRequest = _reflection.GeneratedProtocolMessageType('PAMGenericUidsRequest', (_message.Message,), {
  'DESCRIPTOR' : _PAMGENERICUIDSREQUEST,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMGenericUidsRequest)
  })
_sym_db.RegisterMessage(PAMGenericUidsRequest)

PAMConfiguration = _reflection.GeneratedProtocolMessageType('PAMConfiguration', (_message.Message,), {
  'DESCRIPTOR' : _PAMCONFIGURATION,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMConfiguration)
  })
_sym_db.RegisterMessage(PAMConfiguration)

PAMConfigurations = _reflection.GeneratedProtocolMessageType('PAMConfigurations', (_message.Message,), {
  'DESCRIPTOR' : _PAMCONFIGURATIONS,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMConfigurations)
  })
_sym_db.RegisterMessage(PAMConfigurations)

PAMController = _reflection.GeneratedProtocolMessageType('PAMController', (_message.Message,), {
  'DESCRIPTOR' : _PAMCONTROLLER,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMController)
  })
_sym_db.RegisterMessage(PAMController)

ControllerResponse = _reflection.GeneratedProtocolMessageType('ControllerResponse', (_message.Message,), {
  'DESCRIPTOR' : _CONTROLLERRESPONSE,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.ControllerResponse)
  })
_sym_db.RegisterMessage(ControllerResponse)

PAMConfigurationController = _reflection.GeneratedProtocolMessageType('PAMConfigurationController', (_message.Message,), {
  'DESCRIPTOR' : _PAMCONFIGURATIONCONTROLLER,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.PAMConfigurationController)
  })
_sym_db.RegisterMessage(PAMConfigurationController)

ConfigurationAddRequest = _reflection.GeneratedProtocolMessageType('ConfigurationAddRequest', (_message.Message,), {
  'DESCRIPTOR' : _CONFIGURATIONADDREQUEST,
  '__module__' : 'pam_pb2'
  # @@protoc_insertion_point(class_scope:PAM.ConfigurationAddRequest)
  })
_sym_db.RegisterMessage(ConfigurationAddRequest)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\030com.keepersecurity.protoB\003PAM'
  _PAMOPERATIONTYPE._serialized_start=2032
  _PAMOPERATIONTYPE._serialized_end=2096
  _PAMOPERATIONRESULTTYPE._serialized_start=2098
  _PAMOPERATIONRESULTTYPE._serialized_end=2210
  _CONTROLLERMESSAGETYPE._serialized_start=2212
  _CONTROLLERMESSAGETYPE._serialized_end=2284
  _PAMROTATIONSCHEDULE._serialized_start=37
  _PAMROTATIONSCHEDULE._serialized_end=168
  _PAMROTATIONSCHEDULESRESPONSE._serialized_start=170
  _PAMROTATIONSCHEDULESRESPONSE._serialized_end=245
  _PAMONLINECONTROLLERS._serialized_start=247
  _PAMONLINECONTROLLERS._serialized_end=290
  _PAMROTATEREQUEST._serialized_start=292
  _PAMROTATEREQUEST._serialized_end=349
  _PAMCONTROLLERSRESPONSE._serialized_start=351
  _PAMCONTROLLERSRESPONSE._serialized_end=416
  _PAMREMOVECONTROLLER._serialized_start=418
  _PAMREMOVECONTROLLER._serialized_end=479
  _PAMREMOVECONTROLLERRESPONSE._serialized_start=481
  _PAMREMOVECONTROLLERRESPONSE._serialized_end=557
  _PAMMODIFYREQUEST._serialized_start=559
  _PAMMODIFYREQUEST._serialized_end=620
  _PAMDATAOPERATION._serialized_start=623
  _PAMDATAOPERATION._serialized_end=775
  _PAMCONFIGURATIONDATA._serialized_start=777
  _PAMCONFIGURATIONDATA._serialized_end=878
  _PAMELEMENTDATA._serialized_start=880
  _PAMELEMENTDATA._serialized_end=949
  _PAMELEMENTOPERATIONRESULT._serialized_start=951
  _PAMELEMENTOPERATIONRESULT._serialized_end=1060
  _PAMMODIFYRESULT._serialized_start=1062
  _PAMMODIFYRESULT._serialized_end=1128
  _PAMELEMENT._serialized_start=1130
  _PAMELEMENT._serialized_end=1250
  _PAMGENERICUIDREQUEST._serialized_start=1252
  _PAMGENERICUIDREQUEST._serialized_end=1287
  _PAMGENERICUIDSREQUEST._serialized_start=1289
  _PAMGENERICUIDSREQUEST._serialized_end=1326
  _PAMCONFIGURATION._serialized_start=1329
  _PAMCONFIGURATION._serialized_end=1500
  _PAMCONFIGURATIONS._serialized_start=1502
  _PAMCONFIGURATIONS._serialized_end=1568
  _PAMCONTROLLER._serialized_start=1571
  _PAMCONTROLLER._serialized_end=1826
  _CONTROLLERRESPONSE._serialized_start=1828
  _CONTROLLERRESPONSE._serialized_end=1865
  _PAMCONFIGURATIONCONTROLLER._serialized_start=1867
  _PAMCONFIGURATIONCONTROLLER._serialized_end=1944
  _CONFIGURATIONADDREQUEST._serialized_start=1946
  _CONFIGURATIONADDREQUEST._serialized_end=2030
# @@protoc_insertion_point(module_scope)
