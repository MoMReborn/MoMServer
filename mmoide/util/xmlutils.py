#----------------------------------------------------------------------------

# Name:         xmlutils.py

# Purpose:      XML and Marshaller Utilities

#

# Author:       Jeff Norton

#

# Created:      6/2/05

# CVS-ID:       $Id: xmlutils.py 2530 2005-05-05 21:04:20Z jhare $

# Copyright:    (c) 2004-2005 ActiveGrid, Inc.

# License:      wxWindows License

#----------------------------------------------------------------------------



from mmoide.util.lang import *

import os

import time

import urllib

import logging

from mmoide.util.lang import *

import mmoide.util.objutils as objutils

import mmoide.util.xmlmarshaller as xmlmarshaller

import mmoide.util.aglogging as aglogging



xmlLogger = logging.getLogger("mmoide.util.xml")

    

def load(fileName, knownTypes=None, knownNamespaces=None):

    loadedObject = None

    fileObject = file(fileName)

    timeStart = time.time()

    try:

        xml = fileObject.read()

        loadedObject = unmarshal(xml, knownTypes=knownTypes, knownNamespaces=knownNamespaces, xmlSource=fileName)

        loadedObject.fileName = os.path.abspath(fileName)

        if hasattr(loadedObject, 'initialize'):

            loadedObject.initialize()

    finally:

        fileObject.close()

        timeDone = time.time()

        aglogging.info(xmlLogger, ('Load statistics for file %s: elapsed time = %f secs' % (fileName, timeDone-timeStart)))

    return loadedObject



def loadURI(uri, knownTypes=None, knownNamespaces=None, xmlSource=None):

    loadedObject = None

    xml = urllib.urlopen(uri).read()

    loadedObject = unmarshal(xml, knownTypes=knownTypes, knownNamespaces=knownNamespaces, xmlSource=xmlSource)

    loadedObject.fileName = uri

    if hasattr(loadedObject, 'initialize'):

        loadedObject.initialize()

    return loadedObject



def unmarshal(xml, knownTypes=None, knownNamespaces=None, xmlSource=None):

    if (knownTypes == None): 

        knownTypes, knownNamespaces = getAgKnownTypes()

    return xmlmarshaller.unmarshal(xml, knownTypes=knownTypes, knownNamespaces=knownNamespaces, xmlSource=xmlSource)    



def save(fileName, objectToSave, prettyPrint=True, marshalType=True, knownTypes=None, knownNamespaces=None, encoding='utf-8'):

    if hasattr(objectToSave, '_xmlReadOnly') and objectToSave._xmlReadOnly == True:

        raise xmlmarshaller.MarshallerException('Error marshalling object to file "%s": object is marked "readOnly" and cannot be written' % (fileName))        

    timeStart = time.time()

    xml = marshal(objectToSave, prettyPrint=prettyPrint, marshalType=marshalType, knownTypes=knownTypes, knownNamespaces=knownNamespaces, encoding=encoding)

    fileObject = file(fileName, 'w')

    try:

        fileObject.write(xml)

        fileObject.flush()

    except Exception, errorData:

        fileObject.close()

        raise xmlmarshaller.MarshallerException('Error marshalling object to file "%s": %s' % (fileName, str(errorData)))

    fileObject.close()

    timeDone = time.time()

    aglogging.info(xmlLogger, ('Save statistics for file %s: elapsed time = %f secs' % (fileName, timeDone-timeStart)))

    

def marshal(objectToSave, prettyPrint=True, marshalType=True, knownTypes=None, knownNamespaces=None, encoding='utf-8'):

    if (knownTypes == None): 

        knownTypes, knownNamespaces = getAgKnownTypes()

    return xmlmarshaller.marshal(objectToSave, prettyPrint=prettyPrint, marshalType=marshalType, knownTypes=knownTypes, knownNamespaces=knownNamespaces, encoding=encoding)

    

def addNSAttribute(xmlDoc, shortNamespace, longNamespace):

    if not hasattr(xmlDoc, "__xmlnamespaces__"):

        xmlDoc.__xmlnamespaces__ = {shortNamespace:longNamespace}

    elif shortNamespace not in xmlDoc.__xmlnamespaces__:

        if (hasattr(xmlDoc.__class__, "__xmlnamespaces__") 

            and (xmlDoc.__xmlnamespaces__ is xmlDoc.__class__.__xmlnamespaces__)):

            xmlDoc.__xmlnamespaces__ = dict(xmlDoc.__xmlnamespaces__)

        xmlDoc.__xmlnamespaces__[shortNamespace] = longNamespace



def genShortNS(xmlDoc, longNamespace=None):

    if not hasattr(xmlDoc, "__xmlnamespaces__"):

        return "ns1"

    elif longNamespace != None and longNamespace in xmlDoc.__xmlnamespaces__.items():

        for key, value in xmlDoc.__xmlnamespaces__.iteritems():

            if value == longNamespace:

                return key

    i = 1

    while ("ns%d" % i) in xmlDoc.__xmlnamespaces__:

        i += 1

    return ("ns%d" % i)

    

def genTargetNS(fileName, applicationName=None, type=None):

    if (applicationName != None):

        if (type != None):

            tns = "urn:%s:%s:%s" % (applicationName, type, fileName)

        else:

            tns = "urn:%s:%s" % (applicationName, fileName)

    else:

        tns = "urn:%s" % fileName

    return tns

    

def splitType(typeName):

    index = typeName.rfind(':')

    if index != -1:

        ns = typeName[:index]

        complexTypeName = typeName[index+1:]

    else:

        ns = None

        complexTypeName = typeName

    return (ns, complexTypeName)

        

def cloneObject(objectToClone, knownTypes=None, marshalType=True, knownNamespaces=None, encoding='utf-8'):

    if (knownTypes == None): 

        knownTypes, knownNamespaces = getAgKnownTypes()

    xml = xmlmarshaller.marshal(objectToClone, prettyPrint=True, marshalType=marshalType, knownTypes=knownTypes, knownNamespaces=knownNamespaces, encoding=encoding)

    clonedObject = xmlmarshaller.unmarshal(xml, knownTypes=knownTypes, knownNamespaces=knownNamespaces)

    if hasattr(objectToClone, 'fileName'):

        clonedObject.fileName = objectToClone.fileName

    if hasattr(objectToClone, "_parentDoc"):

        clonedObject._parentDoc = objectToClone._parentDoc

    try:

        clonedObject.initialize()

    except AttributeError:

        pass

    return clonedObject



def getAgVersion(fileName):

    fileObject = file(fileName)

    try:

        xml = fileObject.read()

    finally:

        fileObject.close()

    i = xml.find(' ag:version=')

    if i >= 0:

        i += 12

    else:

        i2 = xml.find('<ag:')

        if i2 >= 0:

            i = xml.find(' version=', i2)

            if i > 0:

                i += 9

        elif xml.find('<project version="10"') >= 0:

            return "10"

        else:

            return None

    version = None

    if xml[i:i+1] == '"':

        j = xml.find('"', i+1)

        if (j > i+1):

            version = xml[i+1:j]

    return version



def escape(data):

    """Escape ', ", &, <, and > in a string of data.



    Basically, everything that saxutils.escape does (and this calls that, at

    least for now), but with " added as well.



    XXX TODO make this faster; saxutils.escape() is really slow

    """



    import xml.sax.saxutils as saxutils



    data=saxutils.escape(data)

    data=data.replace("\"", "&quot;")



    # IE doesn't support &apos;

    # data=data.replace("\'", "&apos;")

    data=data.replace("\'", "&#039;")



    return data



def unescape(data):

    """Unescape ', ", &, <, and > in a string of data.



    Basically, everything that saxutils.unescape does (and this calls that, at

    least for now), but with " added as well.



    XXX TODO make this faster; saxutils.unescape() is really slow

    """



    import xml.sax.saxutils as saxutils



    data=data.replace("&quot;", "\"")

    data=data.replace("&apos;", "\'")

    return saxutils.unescape(data)



    

AG_NS_URL = "http://www.mmoide.com/ag.xsd"

BPEL_NS_URL = "http://schemas.xmlsoap.org/ws/2003/03/business-process"

HTTP_WSDL_NS_URL = "http://schemas.xmlsoap.org/wsdl/http/"

MIME_WSDL_NS_URL = "http://schemas.xmlsoap.org/wsdl/mime/"

SOAP_NS_URL = "http://schemas.xmlsoap.org/wsdl/soap/"

SOAP12_NS_URL = "http://schemas.xmlsoap.org/wsdl/soap12/"

WSDL_NS_URL = "http://schemas.xmlsoap.org/wsdl/"

XFORMS_NS_URL = "http://www.w3c.org/xform.xsd"

XMLSCHEMA_NS_URL = "http://www.w3.org/2001/XMLSchema"

XSI_NS_URL = "http://www.w3.org/2001/XMLSchema-instance"

XACML_NS_URL = "urn:oasis:names:tc:xacml:2.0:policy:schema:os"



KNOWN_NAMESPACES = { AG_NS_URL          :  "ag",

                     BPEL_NS_URL        :  "bpws",

                     HTTP_WSDL_NS_URL   :  "http",

                     MIME_WSDL_NS_URL   :  "mime",

                     SOAP_NS_URL        :  "soap",

                     SOAP12_NS_URL      :  "soap12",

                     WSDL_NS_URL        :  "wsdl", 

                     XFORMS_NS_URL      :  "xforms",                             

                     XMLSCHEMA_NS_URL   :  "xs",

                     XACML_NS_URL       :  "xacml",

                   }

    

global agXsdToClassName

agXsdToClassName = None

def getAgXsdToClassName():

    global agXsdToClassName

    if (agXsdToClassName == None):

        agXsdToClassName = {

            "ag:append"          : "mmoide.model.processmodel.AppendOperation",

            "ag:attribute"       : "mmoide.model.identitymodel.Attribute",

            "ag:body"            : "mmoide.model.processmodel.Body",

            "ag:category_substitutions"    : "mmoide.server.layoutrenderer.CategorySubstitutions",

            "ag:command"         : "mmoide.model.wsdl.Command",

            "ag:css"             : "mmoide.server.layoutrenderer.CSS", 

            "ag:cssRule"         : "mmoide.model.processmodel.CssRule",

            "ag:databaseService" : "mmoide.server.deployment.DatabaseService",

            "ag:datasource"      : "mmoide.data.dataservice.DataSource",

            "ag:dataObjectList"  : "mmoide.data.datalang.DataObjectList",

            "ag:debug"           : "mmoide.model.processmodel.DebugOperation",

            "ag:deployment"      : "mmoide.server.deployment.Deployment",

            "ag:generator"       : "mmoide.server.layoutrenderer.SerializableGenerator", 

            "ag:head"            : "mmoide.server.layoutrenderer.Head", 

            "ag:hr"              : "mmoide.model.processmodel.HorizontalRow",

            "ag:identity"        : "mmoide.model.identitymodel.Identity",

            "ag:identityref"     : "mmoide.server.deployment.IdentityRef",

            "ag:image"           : "mmoide.model.processmodel.Image",

            "ag:label"           : "mmoide.model.processmodel.Label",

            "ag:layout"          : "mmoide.server.layoutrenderer.Layout", 

            "ag:layouts"         : "mmoide.server.layoutrenderer.Layouts", 

            "ag:ldapsource"      : "mmoide.model.identitymodel.LDAPSource",

            "ag:localService"    : "mmoide.server.deployment.LocalService",

            "ag:parameter"       : "mmoide.server.layoutrenderer.Parameter",

            "ag:parameters"      : "mmoide.server.layoutrenderer.Parameters",

            "ag:processref"      : "mmoide.server.deployment.ProcessRef",

            "ag:query"           : "mmoide.model.processmodel.Query",

            "ag:soapService"     : "mmoide.server.deployment.SoapService",

            "ag:requiredFile"    : "mmoide.server.layoutrenderer.RequiredFile", 

            "ag:resource"        : "mmoide.model.identitymodel.IDResource",

            "ag:restService"     : "mmoide.server.deployment.RestService",

            "ag:rewrite"         : "mmoide.model.wsdl.Rewrite",

            "ag:role"            : "mmoide.model.identitymodel.IDRole",

            "ag:roledefn"        : "mmoide.model.identitymodel.RoleDefn",

            "ag:rssService"      : "mmoide.server.deployment.RssService",

            "ag:rule"            : "mmoide.model.identitymodel.IDRule",

            "ag:schemaOptions"   : "mmoide.model.schema.SchemaOptions",

            "ag:schemaref"       : "mmoide.server.deployment.SchemaRef",

            "ag:serviceCache"    : "mmoide.server.deployment.ServiceCache",

            "ag:serviceExtension": "mmoide.model.wsdl.ServiceExtension",

            "ag:serviceExtensions": "mmoide.model.wsdl.ServiceExtensions",

            "ag:serviceParameter": "mmoide.server.deployment.ServiceParameter",

            "ag:serviceref"      : "mmoide.server.deployment.ServiceRef",

            "ag:set"             : "mmoide.model.processmodel.SetOperation",

            "ag:skinref"         : "mmoide.server.deployment.SkinRef",

            "ag:skin"            : "mmoide.server.layoutrenderer.Skin",

            "ag:skin_element_ref": "mmoide.server.layoutrenderer.SkinElementRef",

            "ag:skin_element"    : "mmoide.server.layoutrenderer.SkinElement",

            "ag:skins"           : "mmoide.server.layoutrenderer.Skins",

            "ag:substitution"    : "mmoide.server.layoutrenderer.Substitution", 

            "ag:text"            : "mmoide.model.processmodel.Text",

            "ag:title"           : "mmoide.model.processmodel.Title",

            "ag:usertemplate"    : "mmoide.model.identitymodel.UserTemplate",

            "ag:xformref"        : "mmoide.server.deployment.XFormRef",

            "bpws:case"          : "mmoide.model.processmodel.BPELCase",

            "bpws:catch"         : "mmoide.model.processmodel.BPELCatch",

            "bpws:faultHandlers" : "mmoide.model.processmodel.BPELFaultHandlers",

            "bpws:flow"          : "mmoide.model.processmodel.BPELFlow",

            "bpws:invoke"        : "mmoide.model.processmodel.BPELInvoke",

            "bpws:onMessage"     : "mmoide.model.processmodel.BPELOnMessage",

            "bpws:otherwise"     : "mmoide.model.processmodel.BPELOtherwise",

            "bpws:pick"          : "mmoide.model.processmodel.BPELPick",

            "bpws:process"       : "mmoide.model.processmodel.BPELProcess",

            "bpws:receive"       : "mmoide.model.processmodel.BPELReceive",

            "bpws:reply"         : "mmoide.model.processmodel.BPELReply",

            "bpws:scope"         : "mmoide.model.processmodel.BPELScope",

            "bpws:sequence"      : "mmoide.model.processmodel.BPELSequence",

            "bpws:switch"        : "mmoide.model.processmodel.BPELSwitch",

            "bpws:terminate"     : "mmoide.model.processmodel.BPELTerminate",

            "bpws:variable"      : "mmoide.model.processmodel.BPELVariable",

            "bpws:variables"     : "mmoide.model.processmodel.BPELVariables",

            "bpws:while"         : "mmoide.model.processmodel.BPELWhile",

            "http:address"       : "mmoide.model.wsdl.HttpAddress",

            "http:binding"       : "mmoide.model.wsdl.HttpBinding",

            "http:operation"     : "mmoide.model.wsdl.HttpOperation",

            "http:urlEncoded"    : "mmoide.model.wsdl.HttpUrlEncoded",

            "mime:content"       : "mmoide.model.wsdl.MimeContent",

            "mime:mimeXml"       : "mmoide.model.wsdl.MimeMimeXml",

            "soap:address"       : "mmoide.model.wsdl.SoapAddress",

            "soap:binding"       : "mmoide.model.wsdl.SoapBinding",

            "soap:body"          : "mmoide.model.wsdl.SoapBody",

            "soap:fault"         : "mmoide.model.wsdl.SoapFault",

            "soap:header"        : "mmoide.model.wsdl.SoapHeader",

            "soap:operation"     : "mmoide.model.wsdl.SoapOperation",

            "soap12:address"     : "mmoide.model.wsdl.Soap12Address",

            "soap12:binding"     : "mmoide.model.wsdl.Soap12Binding",

            "soap12:body"        : "mmoide.model.wsdl.Soap12Body",

            "soap12:fault"       : "mmoide.model.wsdl.Soap12Fault",

            "soap12:header"      : "mmoide.model.wsdl.Soap12Header",

            "soap12:operation"   : "mmoide.model.wsdl.Soap12Operation",

            "wsdl:binding"       : "mmoide.model.wsdl.WsdlBinding",

            "wsdl:definitions"   : "mmoide.model.wsdl.WsdlDocument",

            "wsdl:documentation" : "mmoide.model.wsdl.WsdlDocumentation",

            "wsdl:fault"         : "mmoide.model.wsdl.WsdlFault",

            "wsdl:import"        : "mmoide.model.wsdl.WsdlImport",

            "wsdl:input"         : "mmoide.model.wsdl.WsdlInput",

            "wsdl:message"       : "mmoide.model.wsdl.WsdlMessage",

            "wsdl:operation"     : "mmoide.model.wsdl.WsdlOperation",

            "wsdl:output"        : "mmoide.model.wsdl.WsdlOutput",

            "wsdl:part"          : "mmoide.model.wsdl.WsdlPart",

            "wsdl:port"          : "mmoide.model.wsdl.WsdlPort",

            "wsdl:portType"      : "mmoide.model.wsdl.WsdlPortType",

            "wsdl:service"       : "mmoide.model.wsdl.WsdlService",

            "wsdl:types"         : "mmoide.model.wsdl.WsdlTypes",

            "xacml:Action"       : "mmoide.model.identitymodel.XACMLAction",

            "xacml:ActionAttributeDesignator" : "mmoide.model.identitymodel.XACMLActionAttributeDesignator",

            "xacml:ActionMatch"  : "mmoide.model.identitymodel.XACMLActionMatch",

            "xacml:Actions"      : "mmoide.model.identitymodel.XACMLActions",

            "xacml:AttributeValue" : "mmoide.model.identitymodel.XACMLAttributeValue",

            "xacml:Policy"       : "mmoide.model.identitymodel.XACMLPolicy",

            "xacml:Resource"     : "mmoide.model.identitymodel.XACMLResource",

            "xacml:ResourceAttributeDesignator" : "mmoide.model.identitymodel.XACMLResourceAttributeDesignator",

            "xacml:ResourceMatch" : "mmoide.model.identitymodel.XACMLResourceMatch",

            "xacml:Resources"    : "mmoide.model.identitymodel.XACMLResources",

            "xacml:Rule"         : "mmoide.model.identitymodel.XACMLRule",

            "xacml:Target"       : "mmoide.model.identitymodel.XACMLTarget",

            "xforms:copy"        : "mmoide.model.processmodel.XFormsCopy",

            "xforms:group"       : "mmoide.model.processmodel.XFormsGroup",

            "xforms:include"     : "mmoide.model.processmodel.XFormsInclude",

            "xforms:input"       : "mmoide.model.processmodel.XFormsInput",

            "xforms:item"        : "mmoide.model.processmodel.XFormsItem",

            "xforms:itemset"     : "mmoide.model.processmodel.XFormsItemset",

            "xforms:label"       : "mmoide.model.processmodel.XFormsLabel",

            "xforms:model"       : "mmoide.model.processmodel.XFormsModel",

            "xforms:output"      : "mmoide.model.processmodel.XFormsOutput",

            "xforms:secret"      : "mmoide.model.processmodel.XFormsSecret",

            "xforms:select1"     : "mmoide.model.processmodel.XFormsSelect1",

            "xforms:submission"  : "mmoide.model.processmodel.XFormsSubmission",

            "xforms:submit"      : "mmoide.model.processmodel.XFormsSubmit",

            "xforms:value"       : "mmoide.model.processmodel.XFormsValue",

            "xforms:xform"       : "mmoide.model.processmodel.View",

            "xforms:xforms"      : "mmoide.model.processmodel.XFormsRoot",

            "xs:all"             : "mmoide.model.schema.XsdSequence",

            "xs:any"             : "mmoide.model.schema.XsdAny",

            "xs:attribute"       : "mmoide.model.schema.XsdAttribute",

            "xs:complexContent"  : "mmoide.model.schema.XsdComplexContent",

            "xs:complexType"     : "mmoide.model.schema.XsdComplexType",

            "xs:element"         : "mmoide.model.schema.XsdElement",

            "xs:enumeration"     : "mmoide.model.schema.XsdEnumeration",

            "xs:extension"       : "mmoide.model.schema.XsdExtension",

            "xs:field"           : "mmoide.model.schema.XsdKeyField",

            "xs:import"          : "mmoide.model.schema.XsdInclude",

            "xs:include"         : "mmoide.model.schema.XsdInclude",

            "xs:key"             : "mmoide.model.schema.XsdKey",

            "xs:keyref"          : "mmoide.model.schema.XsdKeyRef",

            "xs:length"          : "mmoide.model.schema.XsdLength",

            "xs:list"            : "mmoide.model.schema.XsdList",

            "xs:maxLength"       : "mmoide.model.schema.XsdMaxLength",

            "xs:restriction"     : "mmoide.model.schema.XsdRestriction",

            "xs:schema"          : "mmoide.model.schema.Schema",

            "xs:selector"        : "mmoide.model.schema.XsdKeySelector",              

            "xs:sequence"        : "mmoide.model.schema.XsdSequence",

            "xs:simpleContent"   : "mmoide.model.schema.XsdSimpleContent",

            "xs:simpleType"      : "mmoide.model.schema.XsdSimpleType",

            "xs:totalDigits"     : "mmoide.model.schema.XsdTotalDigits",

        }

    return agXsdToClassName

    

global agKnownTypes

agKnownTypes = None

def getAgKnownTypes():

    global agKnownTypes

    if agKnownTypes == None:

        try:

            tmpAgKnownTypes = {}

            import mmoide.model.processmodel

            import mmoide.model.schema

            import mmoide.server.deployment

            import mmoide.model.wsdl

            ifDefPy()

            import mmoide.data.dataservice

            endIfDef()

            for keyName, className in getAgXsdToClassName().iteritems():

                classType = objutils.classForName(className)

                if (classType == None):

                    raise Exception("Cannot get class type for %s" % className)

                else:

                    tmpAgKnownTypes[keyName] = classType

            if len(tmpAgKnownTypes) > 0:

                agKnownTypes = tmpAgKnownTypes

        except ImportError:

            agKnownTypes = {}

    if len(agKnownTypes) == 0:     # standalone IDE and XmlMarshaller don't contain known AG types

        noKnownNamespaces = {}

        return agKnownTypes, noKnownNamespaces            

    return agKnownTypes, KNOWN_NAMESPACES

