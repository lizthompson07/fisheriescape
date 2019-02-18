from django.db.models import Q
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, fromstring
from xml.etree import ElementTree
from xml.dom import minidom
from django.utils import timezone
from . import models
from django.urls import reverse


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8")


def charstring(root, level_1_tag, text_eng, text_fre=None):
    """Takes in the root and creates a charstring tag in the root. If text_fre is missing it will be a unilingual element.
        """
    if text_fre == None:
        level_1 = SubElement(root, level_1_tag)
        CharacterString = SubElement(level_1, 'gco:CharacterString').text = text_eng
    else:
        level_1 = SubElement(root, level_1_tag, attrib={
            'xsi:type': "gmd:PT_FreeText_PropertyType",
        })
        SubElement(level_1, 'gco:CharacterString').text = text_eng
        PT_FreeText = SubElement(level_1, 'gmd:PT_FreeText')
        textGroup = SubElement(PT_FreeText, 'gmd:textGroup')
        LocalisedCharacterString = SubElement(textGroup, 'gmd:LocalisedCharacterString', attrib={
            'locale': "#fra"
        }).text = text_fre
    return None


def date_converter(year, month=None, day=None):
    if day != None:
        date_string = "{}-{}-{}".format(str(year).zfill(4), str(month).zfill(2), str(day).zfill(2))
    elif month != None:
        date_string = "{}-{}".format(str(year).zfill(4), str(month).zfill(2))
    else:
        date_string = "{}".format(str(year).zfill(4))
    return date_string


def datestamp(root, level_1_tag, year, month=None, day=None):
    date_string = date_converter(year, month, day)
    level_1 = SubElement(root, level_1_tag)
    datestamp = SubElement(level_1, 'gco:Date').text = date_string  # DJF modified this from DateTime to Date
    return None


def codelist(root, level_1_tag, level_2_tag, code_list, code_list_value, text):
    element = SubElement(SubElement(root, level_1_tag), level_2_tag, attrib={
        'codeList': code_list,
        'codeListValue': code_list_value,
    }).text = text
    return None


def ci_responsible_party(resource_person):
    root = Element('gmd:CI_ResponsibleParty')

    # individualName
    charstring(root, 'gmd:individualName', resource_person.person.full_name)

    # organisationName
    charstring(root, 'gmd:organisationName', resource_person.person.organization.name_eng,
               resource_person.person.organization.name_fre)

    # positionName
    charstring(root, 'gmd:positionName', resource_person.person.position_eng, resource_person.person.position_fre)

    contact_info = SubElement(root, "gmd:contactInfo")
    ci_contact = SubElement(contact_info, "gmd:CI_Contact")
    # telephone
    phone = SubElement(ci_contact, "gmd:phone")
    ci_telephone = SubElement(phone, "gmd:CI_Telephone")
    charstring(ci_telephone, 'gmd:voice', resource_person.person.phone, resource_person.person.phone)
    # address
    address = SubElement(ci_contact, "gmd:address")
    ci_address = SubElement(address, "gmd:CI_Address")
    # civic
    charstring(ci_address, 'gmd:deliveryPoint', resource_person.person.organization.address,
               resource_person.person.organization.address)
    # city
    charstring(ci_address, 'gmd:city', resource_person.person.organization.city)
    # province
    charstring(ci_address, 'gmd:administrativeArea', resource_person.person.organization.location.location_eng,
               resource_person.person.organization.location.location_fre)
    # postalcode
    charstring(ci_address, 'gmd:postalCode', resource_person.person.organization.postal_code)
    # country
    charstring(ci_address, 'gmd:country', resource_person.person.organization.location.country,
               resource_person.person.organization.location.country)
    # email
    charstring(ci_address, 'gmd:electronicMailAddress', resource_person.person.user.email,
               resource_person.person.user.email)
    # role
    codelist(root, "gmd:role", "gmd:CI_RoleCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_90", resource_person.role.code,
             resource_person.role.role)
    return root


def descriptive_keyword(keyword):
    """ returns an xml block for a single keyword
    """
    if keyword.text_value_fre == None:
        print("There is no french version of the keyword '{}'".format(keyword.text_value_eng))

    root = Element('gmd:keyword', attrib={
        'xmlns:gmd': "http://www.isotc211.org/2005/gmd",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:type': "gmd:PT_FreeText_PropertyType",
    })
    SubElement(root, 'gco:CharacterString', attrib={
        'xmlns:gco': "http://www.isotc211.org/2005/gco",
    }).text = keyword.text_value_eng
    PT_FreeText = SubElement(root, 'gmd:PT_FreeText')
    textGroup = SubElement(PT_FreeText, 'gmd:textGroup')
    LocalisedCharacterString = SubElement(textGroup, 'gmd:LocalisedCharacterString', attrib={
        'locale': "#fra"
    }).text = keyword.text_value_fre
    return root


class SupplemantInformation:
    def __init__(self, resource):
        self.resource = resource

    # list of fields to build #
    ##########################
    # parameters collected
    # QC process description
    # Physical sample description
    # citations

    def create_english_block(self):
        xml_block = ""
        # parameters collected
        if self.resource.parameters_collected_eng != None and self.resource.parameters_collected_eng != "":
            xml_temp = "PARAMETERS COLLECTED:\n{}".format(self.resource.parameters_collected_eng)
            if xml_block == None:
                xml_block = xml_temp
            else:
                xml_block = "{}\n\n{}".format(xml_block, xml_temp)

        # QC process description
        if self.resource.qc_process_descr_eng != None and self.resource.qc_process_descr_eng != "":
            xml_temp = "NOTES ON QUALITY CONTROL:\n{}".format(self.resource.qc_process_descr_eng)
            if xml_block == None:
                xml_block = xml_temp
            else:
                xml_block = "{}\n\n{}".format(xml_block, xml_temp)

        # Physical sample description
        if self.resource.physical_sample_descr_eng != None and self.resource.physical_sample_descr_eng != "":
            xml_temp = "PHYSICAL SAMPLE DETAILS:\n{}".format(self.resource.physical_sample_descr_eng)
            if xml_block == None:
                xml_block = xml_temp
            else:
                xml_block = "{}\n\n{}".format(xml_block, xml_temp)

        # citations
        if self.resource.citations.count() > 0:
            citation_list = ""
            for citation in self.resource.citations.all():
                if citation_list == "":
                    citation_list = "{}".format(citation.short_citation)
                else:
                    citation_list = "{}\n\n{}".format(citation_list, citation.short_citation)

            xml_temp = "CITATION LIST:\n{}".format(citation_list)
            if xml_block == None:
                xml_block = xml_temp
            else:
                xml_block = "{}\n\n{}".format(xml_block, xml_temp)
        return xml_block

    def create_french_block(self):
        xml_block = ""
        # parameters collected
        if self.resource.parameters_collected_fre != None and self.resource.parameters_collected_fre != "":
            xml_temp = "PARAMÈTRES COLLECTÉS :\n{}".format(self.resource.parameters_collected_fre)
            if xml_block == None:
                xml_block = xml_temp
            else:
                xml_block = "{}\n\n{}".format(xml_block, xml_temp)

        # QC process description
        if self.resource.qc_process_descr_fre != None and self.resource.qc_process_descr_fre != "":
            xml_temp = "NOTES SUR LE CONTRÔLE DE QUALITÉ :\n{}".format(self.resource.qc_process_descr_fre)
            if xml_block == None:
                xml_block = xml_temp
            else:
                xml_block = "{}\n\n{}".format(xml_block, xml_temp)

        # Physical sample description
        if self.resource.physical_sample_descr_fre != None and self.resource.physical_sample_descr_fre != "":
            xml_temp = "DÉTAILS DE L'ÉCHANTILLON PHYSIQUE :\n{}".format(self.resource.physical_sample_descr_fre)
            if xml_block == None:
                xml_block = xml_temp
            else:
                xml_block = "{}\n\n{}".format(xml_block, xml_temp)

        # citations
        if self.resource.citations.count() > 0:
            citation_list = ""
            for citation in self.resource.citations.all():
                if citation_list == "":
                    citation_list = "{}".format(citation.short_citation)
                else:
                    citation_list = "{}\n\n{}".format(citation_list, citation.short_citation)

            xml_temp = "LISTE DE RÉFÉRENCE :\n{}".format(citation_list)
            if xml_block == None:
                xml_block = xml_temp
            else:
                xml_block = "{}\n\n{}".format(xml_block, xml_temp)

        return xml_block


class KeywordGroup:
    def __init__(self, resource, domain):
        self.keywords = resource.keywords.filter(keyword_domain_id=domain)
        self.domain = domain
        self.keyword_count = len(self.keywords)

    def create_topic_category(self, root):
        """returns an xml element for the whole topicCategory domain
        """
        for keyword in self.keywords:
            topicCategory = SubElement(root, 'gmd:topicCategory')
            MD_TopicCategoryCode = SubElement(topicCategory, 'gmd:MD_TopicCategoryCode')
            MD_TopicCategoryCode.text = keyword.text_value_eng

    def create_group_element(self):
        """returns an xml element for the whole keyword domain
        """
        descriptiveKeywords = Element('gmd:descriptiveKeywords')
        MD_Keywords = SubElement(descriptiveKeywords, 'gmd:MD_Keywords')

        # for each keyword add a keyword block using nested function
        for keyword in self.keywords:
            MD_Keywords.append(descriptive_keyword(keyword))

        # annotation #
        ##############
        if self.domain == 1:  # NASA good
            codelist(MD_Keywords, "gmd:type", "gmd:MD_KeywordTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_101", "RI_528",
                     "theme; thème")
            thesaurusName = SubElement(MD_Keywords, 'gmd:thesaurusName')
            CI_Citation = SubElement(thesaurusName, 'gmd:CI_Citation')
            charstring(CI_Citation, 'gmd:title',
                       "NASA/Global Change Master Directory (GCMD) Science Keywords Version 6.0.0.0.0",
                       "NASA/Global Change Master Directory (GCMD) Science Keywords Version 6.0.0.0.0")
            # revision date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2007)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_368",
                     "revision; révision")
            # publication date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2007)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                     "publication; publication")
            # creation date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2007)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_366",
                     "creation;création")
            citedResponsibleParty = SubElement(CI_Citation, 'gmd:citedResponsibleParty')
            CI_ResponsibleParty = SubElement(citedResponsibleParty, 'gmd:CI_ResponsibleParty')
            charstring(CI_ResponsibleParty, 'gmd:individualName',
                       'LM Olsen, G Major, K Shein, J Scialdone, R Vogel, S Leicester, H Weir, S Ritz, T Stevens, M Meaux, C Solomon, R Bilodeau, M Holland, T Northcutt, RA Restrepo')
            charstring(CI_ResponsibleParty, 'gmd:organisationName', 'NASA', 'NASA')
            contactInfo = SubElement(CI_ResponsibleParty, 'gmd:contactInfo')
            CI_Contact = SubElement(contactInfo, 'gmd:CI_Contact')
            onlineResource = SubElement(CI_Contact, 'gmd:onlineResource')
            CI_OnlineResource = SubElement(onlineResource, 'gmd:CI_OnlineResource')
            linkage = SubElement(CI_OnlineResource, 'gmd:linkage')
            url = SubElement(linkage, 'gmd:URL')
            url.text = "http://gcmd.nasa.gov/index.html"
            charstring(CI_OnlineResource, 'gmd:protocol', 'WWW:LINK-1.0-http--link')
            codelist(CI_ResponsibleParty, "gmd:role", "gmd:CI_RoleCode",
                     "http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode", 'owner', 'Owner')


        elif self.domain == 2:  # ITIS
            codelist(MD_Keywords, "gmd:type", "gmd:MD_KeywordTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_101", "RI_528",
                     "theme; thème")
            thesaurusName = SubElement(MD_Keywords, 'gmd:thesaurusName')
            CI_Citation = SubElement(thesaurusName, 'gmd:CI_Citation')
            charstring(CI_Citation, 'gmd:title', "Integrated Taxonomic Information System (ITIS)",
                       "Integrated Taxonomic Information System (ITIS)")
            # revision date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2017)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_368",
                     "revision; révision")
            # publication date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2017)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                     "publication; publication")
            # creation date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2017)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_366",
                     "creation;création")
            citedResponsibleParty = SubElement(CI_Citation, 'gmd:citedResponsibleParty')
            CI_ResponsibleParty = SubElement(citedResponsibleParty, 'gmd:CI_ResponsibleParty')
            charstring(CI_ResponsibleParty, 'gmd:organisationName', 'Integrated Taxonomic Information System (ITIS)',
                       'Integrated Taxonomic Information System (ITIS)')
            contactInfo = SubElement(CI_ResponsibleParty, 'gmd:contactInfo')
            CI_Contact = SubElement(contactInfo, 'gmd:CI_Contact')
            onlineResource = SubElement(CI_Contact, 'gmd:onlineResource')
            CI_OnlineResource = SubElement(onlineResource, 'gmd:CI_OnlineResource')
            linkage = SubElement(CI_OnlineResource, 'gmd:linkage')
            url = SubElement(linkage, 'gmd:URL')
            url.text = "https://www.itis.gov"
            charstring(CI_OnlineResource, 'gmd:protocol', 'WWW:LINK-1.0-http--link')
            codelist(CI_ResponsibleParty, "gmd:role", "gmd:CI_RoleCode",
                     "http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode", 'owner', 'Owner')

        elif self.domain == 3:  # MeSH
            codelist(MD_Keywords, "gmd:type", "gmd:MD_KeywordTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_101", "RI_528",
                     "theme; thème")
            thesaurusName = SubElement(MD_Keywords, 'gmd:thesaurusName')
            CI_Citation = SubElement(thesaurusName, 'gmd:CI_Citation')
            charstring(CI_Citation, 'gmd:title', "Medical Subject Headings (MeSH)", "Medical Subject Headings (MeSH)")
            # revision date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_368",
                     "revision; révision")
            # publication date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                     "publication; publication")
            # creation date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_366",
                     "creation;création")
            citedResponsibleParty = SubElement(CI_Citation, 'gmd:citedResponsibleParty')
            CI_ResponsibleParty = SubElement(citedResponsibleParty, 'gmd:CI_ResponsibleParty')
            charstring(CI_ResponsibleParty, 'gmd:organisationName', 'U.S. National Library of Medicine',
                       'U.S. National Library of Medicine')
            contactInfo = SubElement(CI_ResponsibleParty, 'gmd:contactInfo')
            CI_Contact = SubElement(contactInfo, 'gmd:CI_Contact')
            onlineResource = SubElement(CI_Contact, 'gmd:onlineResource')
            CI_OnlineResource = SubElement(onlineResource, 'gmd:CI_OnlineResource')
            linkage = SubElement(CI_OnlineResource, 'gmd:linkage')
            url = SubElement(linkage, 'gmd:URL')
            url.text = "https://www.nlm.nih.gov/mesh/"
            charstring(CI_OnlineResource, 'gmd:protocol', 'WWW:LINK-1.0-http--link')
            codelist(CI_ResponsibleParty, "gmd:role", "gmd:CI_RoleCode",
                     "http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode", 'owner', 'Owner')

        elif self.domain == 4:  # Uncontrolled
            codelist(MD_Keywords, "gmd:type", "gmd:MD_KeywordTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_101", "RI_528",
                     "theme; thème")
            thesaurusName = SubElement(MD_Keywords, 'gmd:thesaurusName')
            CI_Citation = SubElement(thesaurusName, 'gmd:CI_Citation')
            charstring(CI_Citation, 'gmd:title', "uncontrolled vocabulary; user-specified",
                       "vocabulaire libre; spécifié par l'utilisateur")
            # revision date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_368",
                     "revision; révision")
            # publication date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                     "publication; publication")
            # creation date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_366",
                     "creation;création")
            citedResponsibleParty = SubElement(CI_Citation, 'gmd:citedResponsibleParty')
            CI_ResponsibleParty = SubElement(citedResponsibleParty, 'gmd:CI_ResponsibleParty')
            charstring(CI_ResponsibleParty, 'gmd:organisationName', 'n/a', 'n/a')
            codelist(CI_ResponsibleParty, "gmd:role", "gmd:CI_RoleCode",
                     "http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode", 'owner', 'Owner')


        elif self.domain == 5:  # WoRMS
            codelist(MD_Keywords, "gmd:type", "gmd:MD_KeywordTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_101", "RI_528",
                     "theme; thème")
            thesaurusName = SubElement(MD_Keywords, 'gmd:thesaurusName')
            CI_Citation = SubElement(thesaurusName, 'gmd:CI_Citation')
            charstring(CI_Citation, 'gmd:title', "World Register of Marine Species (WoRMS)",
                       "World Register of Marine Species (WoRMS)")
            # revision date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_368",
                     "revision; révision")
            # publication date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                     "publication; publication")
            # creation date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2018)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_366",
                     "creation;création")
            citedResponsibleParty = SubElement(CI_Citation, 'gmd:citedResponsibleParty')
            CI_ResponsibleParty = SubElement(citedResponsibleParty, 'gmd:CI_ResponsibleParty')
            charstring(CI_ResponsibleParty, 'gmd:organisationName', 'World Register of Marine Species',
                       'World Register of Marine Species')
            contactInfo = SubElement(CI_ResponsibleParty, 'gmd:contactInfo')
            CI_Contact = SubElement(contactInfo, 'gmd:CI_Contact')
            onlineResource = SubElement(CI_Contact, 'gmd:onlineResource')
            CI_OnlineResource = SubElement(onlineResource, 'gmd:CI_OnlineResource')
            linkage = SubElement(CI_OnlineResource, 'gmd:linkage')
            url = SubElement(linkage, 'gmd:URL')
            url.text = "http://www.marinespecies.org/"
            charstring(CI_OnlineResource, 'gmd:protocol', 'WWW:LINK-1.0-http--link')
            codelist(CI_ResponsibleParty, "gmd:role", "gmd:CI_RoleCode",
                     "http://www.isotc211.org/2005/resources/Codelist/gmxCodelists.xml#CI_RoleCode", 'owner', 'Owner')

        elif self.domain == 6:  # core subject
            codelist(MD_Keywords, "gmd:type", "gmd:MD_KeywordTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_101", "RI_528",
                     "theme; thème")
            thesaurusName = SubElement(MD_Keywords, 'gmd:thesaurusName')
            CI_Citation = SubElement(thesaurusName, 'gmd:CI_Citation')
            charstring(CI_Citation, 'gmd:title', "Government of Canada Core Subject Thesaurus",
                       "Thésaurus des sujets de base du gouvernement du Canada")
            # creation date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2004)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_366",
                     "creation; création")
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2016, 7, 4)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_368",
                     "revision; révision")
            # publication date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2007, 7, 23)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                     "publication; publication")
            citedResponsibleParty = SubElement(CI_Citation, 'gmd:citedResponsibleParty')
            CI_ResponsibleParty = SubElement(citedResponsibleParty, 'gmd:CI_ResponsibleParty')
            charstring(CI_ResponsibleParty, 'gmd:organisationName', 'Government of Canada; Library and Archives Canada',
                       'Gouvernement du Canada; Bibliothèque et Archives Canada')
            contactInfo = SubElement(CI_ResponsibleParty, 'gmd:contactInfo')
            CI_Contact = SubElement(contactInfo, 'gmd:CI_Contact')
            onlineResource = SubElement(CI_Contact, 'gmd:onlineResource')
            CI_OnlineResource = SubElement(onlineResource, 'gmd:CI_OnlineResource')
            linkage = SubElement(CI_OnlineResource, 'gmd:linkage')
            url = SubElement(linkage, 'gmd:URL')
            url.text = "http://canada.multites.net"
            charstring(CI_OnlineResource, 'gmd:protocol', 'WWW:LINK-1.0-http--link')
            codelist(CI_ResponsibleParty, "gmd:role", "gmd:CI_RoleCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_90", 'RI_409',
                     'custodian; conservateur')

        elif self.domain == 7:  # DFO areas
            codelist(MD_Keywords, "gmd:type", "gmd:MD_KeywordTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_101", "RI_525", "place")
            thesaurusName = SubElement(MD_Keywords, 'gmd:thesaurusName')
            CI_Citation = SubElement(thesaurusName, 'gmd:CI_Citation')
            charstring(CI_Citation, 'gmd:title', "DFO Areas", "Zones du MPO")
            # revision date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2009, 1, 6)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_368",
                     "revision; révision")
            # publication date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2009)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                     "publication; publication")
            # creation date
            date = SubElement(CI_Citation, 'gmd:date')
            CI_Date = SubElement(date, 'gmd:CI_Date')
            datestamp(CI_Date, 'gmd:date', 2009)
            codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_366",
                     "creation;création")
            citedResponsibleParty = SubElement(CI_Citation, 'gmd:citedResponsibleParty')
            CI_ResponsibleParty = SubElement(citedResponsibleParty, 'gmd:CI_ResponsibleParty')
            charstring(CI_ResponsibleParty, 'gmd:individualName', 'Doug Gregory')
            charstring(CI_ResponsibleParty, 'gmd:organisationName', 'Government of Canada; Fisheries and Oceans Canada',
                       'Gouvernement du Canada; Pêches et Océans Canada')
            contactInfo = SubElement(CI_ResponsibleParty, 'gmd:contactInfo')
            CI_Contact = SubElement(contactInfo, 'gmd:CI_Contact')
            onlineResource = SubElement(CI_Contact, 'gmd:onlineResource')
            CI_OnlineResource = SubElement(onlineResource, 'gmd:CI_OnlineResource')
            linkage = SubElement(CI_OnlineResource, 'gmd:linkage')
            url = SubElement(linkage, 'gmd:URL')
            url.text = "http://gcmd.nasa.gov/index.html"
            charstring(CI_OnlineResource, 'gmd:protocol', 'WWW:LINK-1.0-http--link')
            codelist(CI_ResponsibleParty, "gmd:role", "gmd:CI_RoleCode",
                     "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_90", 'RI_413',
                     'originator; créateur')

        return descriptiveKeywords


def construct(my_resource):
    # ElementTree.register_namespace("gmd","http://www.isotc211.org/2005/gmd")
    # ElementTree.register_namespace("xsi","http://www.w3.org/2001/XMLSchema-instance")

    root = Element("gmd:MD_Metadata", attrib={
        "xmlns:gmd": "http://www.isotc211.org/2005/gmd",
        'xmlns:srv': "http://www.isotc211.org/2005/srv",
        'xmlns:gss': "http://www.isotc211.org/2005/gss",
        'xmlns:gco': "http://www.isotc211.org/2005/gco",
        'xmlns:xlink': "http://www.w3.org/1999/xlink",
        'xmlns:gts': "http://www.isotc211.org/2005/gts",
        'xmlns:gfc': "http://www.isotc211.org/2005/gfc",
        'xmlns:gmi': "http://www.isotc211.org/2005/gmi",
        'xmlns:gml': "http://www.opengis.net/gml/3.2",
        'xmlns:gmx': "http://www.isotc211.org/2005/gmx",
        'xmlns:gsr': "http://www.isotc211.org/2005/gsr",
        'xmlns': "http://www.isotc211.org/2005/gmd",
        'xmlns:geonet': "http://www.fao.org/geonetwork",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemaLocation': "http://www.isotc211.org/2005/gmd http://nap.geogratis.gc.ca/metadata/tools/schemas/metadata/can-cgsb-171.100-2009-a/gmd/gmd.xsd http://www.isotc211.org/2005/srv http://nap.geogratis.gc.ca/metadata/tools/schemas/metadata/can-cgsb-171.100-2009-a/srv/srv.xsd http://www.geconnections.org/nap/napMetadataTools/napXsd/napm http://nap.geogratis.gc.ca/metadata/tools/schemas/metadata/can-cgsb-171.100-2009-a/napm/napm.xsd",

    })

    # uuid
    charstring(root, 'gmd:fileIdentifier', str(my_resource.uuid))

    # language
    charstring(root, 'gmd:language', "eng; CAN")

    # characterSet for metadata
    codelist(root, "gmd:characterSet", "gmd:MD_CharacterSetCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_95", "RI_458", "utf8; utf8")

    # parentIdentifier
    if my_resource.parent != None:
        charstring(root, 'gmd:parentIdentifier', str(my_resource.parent.uuid))

    # ResourceType
    codelist(root, "gmd:hierarchyLevel", "gmd:MD_ScopeCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_108",
             my_resource.resource_type.code, my_resource.resource_type.label)

    # responsible parties for metadata information
    gmd_contact = SubElement(root, 'gmd:contact')

    # for each point of contact
    for person in my_resource.resource_people.all():
        if person.role.id == 4:
            gmd_contact.append(ci_responsible_party(person))

    # timestamp
    datestamp(root, 'gmd:dateStamp', timezone.now().year, timezone.now().month, timezone.now().day)

    # metadata standard name - STATIC
    charstring(root, 'gmd:metadataStandardName',
               "North American Profile of ISO 19115:2003 - Geographic information - Metadata",
               "Profil nord-américain de la norme ISO 19115:2003 - Information géographique - Métadonnées")

    # metadata standards version - STATIC
    charstring(root, 'gmd:metadataStandardVersion', "CAN/CGSB-171.100-2009")

    # locale - STATIC
    PT_Locale = SubElement(SubElement(root, 'gmd:locale'), "gmd:PT_Locale", attrib={'id': "fra"})
    codelist(PT_Locale, "gmd:languageCode", "gmd:LanguageCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_116", "fra", "French; Français")
    codelist(PT_Locale, "gmd:Country", "gmd:Country",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_117", "CAN", "Canada; Canada")
    codelist(PT_Locale, "gmd:characterEncoding", "gmd:MD_CharacterSetCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_458", "RI_458", "utf8; utf8")

    # Reference system info
    referenceSystemInfo = SubElement(root, 'gmd:referenceSystemInfo')
    MD_ReferenceSystem = SubElement(referenceSystemInfo, 'gmd:MD_ReferenceSystem')
    referenceSystemIdentifier = SubElement(MD_ReferenceSystem, 'gmd:referenceSystemIdentifier')
    RS_Identifier = SubElement(referenceSystemIdentifier, 'gmd:RS_Identifier')

    try:
        charstring(RS_Identifier, 'gmd:code', my_resource.spat_ref_system.code)
        charstring(RS_Identifier, 'gmd:codeSpace', my_resource.spat_ref_system.codespace)
    except Exception as e:
        print("no spat_ref_system")

    # Data identification Info #
    ############################

    identificationInfo = SubElement(root, 'gmd:identificationInfo')
    MD_DataIdentification = SubElement(identificationInfo, 'gmd:MD_DataIdentification')
    citation = SubElement(MD_DataIdentification, 'gmd:citation')
    CI_Citation = SubElement(citation, 'gmd:CI_Citation')

    # Title
    charstring(CI_Citation, 'gmd:title', my_resource.title_eng, my_resource.title_fre)

    # creation date
    CI_Date = SubElement(SubElement(CI_Citation, 'gmd:date'), 'gmd:CI_Date')
    datestamp(CI_Date, 'gmd:date', my_resource.time_start_year, my_resource.time_start_month,
              my_resource.time_start_day)
    codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_366",
             "creation; création")

    if my_resource.fgp_publication_date == None:  # only pass in a publication date, which would be the current time

        # publication date
        CI_Date = SubElement(SubElement(CI_Citation, 'gmd:date'), 'gmd:CI_Date')
        datestamp(CI_Date, 'gmd:date', timezone.now().year, timezone.now().month, timezone.now().day)
        codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                 "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                 "publication; publication")

    else:  # publication AND revision dates are added

        # publication date
        CI_Date = SubElement(SubElement(CI_Citation, 'gmd:date'), 'gmd:CI_Date')
        datestamp(CI_Date, 'gmd:date', my_resource.fgp_publication_date.year, my_resource.fgp_publication_date.month,
                  my_resource.fgp_publication_date.day)
        codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                 "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_367",
                 "publication; publication")

        # revision date
        CI_Date = SubElement(SubElement(CI_Citation, 'gmd:date'), 'gmd:CI_Date')
        datestamp(CI_Date, 'gmd:date', timezone.now().year, timezone.now().month, timezone.now().day)
        codelist(CI_Date, "gmd:dateType", "gmd:CI_DateTypeCode",
                 "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_87", "RI_368",
                 "revision; révision")

    # Custodians
    citedResponsibleParty = SubElement(CI_Citation, 'gmd:citedResponsibleParty')
    # for each point of contact
    for person in my_resource.resource_people.all():
        if person.role.id == 1:
            citedResponsibleParty.append(ci_responsible_party(person))

    # abstract
    charstring(MD_DataIdentification, 'gmd:abstract', my_resource.descr_eng, my_resource.descr_fre)

    # purpose
    charstring(MD_DataIdentification, 'gmd:purpose', my_resource.purpose_eng, my_resource.purpose_fre)

    # status
    codelist(MD_DataIdentification, "gmd:status", "gmd:MD_ProgressCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_106", my_resource.status.code,
             my_resource.status.label)

    # resource Maintenance
    MD_MaintenanceInformation = SubElement(SubElement(MD_DataIdentification, 'gmd:resourceMaintenance'),
                                           'gmd:MD_MaintenanceInformation')
    codelist(MD_MaintenanceInformation, "gmd:maintenanceAndUpdateFrequency", "gmd:MD_MaintenanceFrequencyCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_102",
             my_resource.maintenance.code, my_resource.maintenance.code)

    # uncontrolled
    uncontrolled = KeywordGroup(my_resource, 4)
    if uncontrolled.keyword_count > 0:
        MD_DataIdentification.append(uncontrolled.create_group_element())

    # GCMD
    gcmd = KeywordGroup(my_resource, 1)
    if gcmd.keyword_count > 0:
        MD_DataIdentification.append(gcmd.create_group_element())

    # DFO areas
    dfo_area = KeywordGroup(my_resource, 7)
    if dfo_area.keyword_count > 0:
        MD_DataIdentification.append(dfo_area.create_group_element())

    # gc core subject
    gc_core = KeywordGroup(my_resource, 6)
    if gc_core.keyword_count > 0:
        MD_DataIdentification.append(gc_core.create_group_element())

    # ITIS
    itis = KeywordGroup(my_resource, 2)
    if itis.keyword_count > 0:
        MD_DataIdentification.append(itis.create_group_element())

    # MeSH
    mesh = KeywordGroup(my_resource, 3)
    if mesh.keyword_count > 0:
        MD_DataIdentification.append(mesh.create_group_element())

    # WoRMS
    worms = KeywordGroup(my_resource, 5)
    if worms.keyword_count > 0:
        MD_DataIdentification.append(worms.create_group_element())

    # LegalConstraints - STATIC
    MD_LegalConstraints = SubElement(SubElement(MD_DataIdentification, 'gmd:resourceConstraints'),
                                     'gmd:MD_LegalConstraints')
    charstring(MD_LegalConstraints, 'gmd:useLimitation',
               "Open Government Licence - Canada (http://open.canada.ca/en/open-government-licence-canada)",
               "Licence du gouvernement ouvert - Canada (http://ouvert.canada.ca/fr/licence-du-gouvernement-ouvert-canada)")
    codelist(MD_LegalConstraints, "gmd:accessConstraints", "gmd:MD_RestrictionCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_107", "RI_606",
             "license; licence")
    codelist(MD_LegalConstraints, "gmd:useConstraints", "gmd:MD_RestrictionCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_107", "RI_606",
             "license; licence")

    # General Constraints
    MD_Constraints = SubElement(SubElement(MD_DataIdentification, 'gmd:resourceConstraints'), 'gmd:MD_Constraints')
    charstring(MD_Constraints, 'gmd:useLimitation', my_resource.resource_constraint_eng,
               my_resource.resource_constraint_fre)

    # Security Constraints
    MD_SecurityConstraints = SubElement(SubElement(MD_DataIdentification, 'gmd:resourceConstraints'),
                                        'gmd:MD_SecurityConstraints')
    charstring(MD_SecurityConstraints, 'gmd:useLimitation', my_resource.security_use_limitation_eng,
               my_resource.security_use_limitation_fre)
    codelist(MD_SecurityConstraints, "gmd:classification", "gmd:MD_ClassificationCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_96", "RI_484",
             "Unclassified; non-classifié")

    # spatialRepresentationType
    try:
        codelist(MD_DataIdentification, "gmd:spatialRepresentationType", "gmd:MD_SpatialRepresentationTypeCode",
                 "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_109",
                 my_resource.spat_representation.code, my_resource.spat_representation.label)
    except Exception as e:
        print("No 'spat_representation'")

        # language
    charstring(MD_DataIdentification, 'gmd:language', 'eng; CAN')

    # characterSet
    codelist(MD_DataIdentification, "gmd:characterSet", "gmd:MD_CharacterSetCode",
             "http://nap.geogratis.gc.ca/metadata/register/napMetadataRegister.xml#IC_195",
             my_resource.data_char_set.code, my_resource.data_char_set.label)

    # topic category
    topic_category = KeywordGroup(my_resource, 8)
    if topic_category.keyword_count > 0:
        topic_category.create_topic_category(MD_DataIdentification)

    # temporal extent
    extent = SubElement(MD_DataIdentification, 'gmd:extent')
    EX_Extent = SubElement(extent, 'gmd:EX_Extent')
    temporalElement = SubElement(EX_Extent, 'gmd:temporalElement')
    EX_TemporalExtent = SubElement(temporalElement, 'gmd:EX_TemporalExtent')
    extent = SubElement(EX_TemporalExtent, 'gmd:extent')
    TimePeriod = SubElement(extent, 'gml:TimePeriod', attrib={'gml:id': "timeperiod1"})
    beginPosition = SubElement(TimePeriod, 'gml:beginPosition')
    endPosition = SubElement(TimePeriod, 'gml:endPosition')
    beginPosition.text = date_converter(my_resource.time_start_year, my_resource.time_start_month,
                                        my_resource.time_start_day)
    if my_resource.time_end_year != None:
        endPosition.text = date_converter(my_resource.time_end_year, my_resource.time_end_month,
                                          my_resource.time_end_day)

    # geographic extent
    extent = SubElement(MD_DataIdentification, 'gmd:extent')
    EX_Extent = SubElement(extent, 'gmd:EX_Extent')
    charstring(EX_Extent, 'gmd:description', my_resource.geo_descr_eng, my_resource.geo_descr_fre)

    geographicElement = SubElement(EX_Extent, 'gmd:geographicElement')
    EX_GeographicBoundingBox = SubElement(geographicElement, 'gmd:EX_GeographicBoundingBox')
    westBoundLongitude = SubElement(EX_GeographicBoundingBox, 'gmd:westBoundLongitude')
    SubElement(westBoundLongitude, 'gco:Decimal').text = str(my_resource.west_bounding)
    eastBoundLongitude = SubElement(EX_GeographicBoundingBox, 'gmd:eastBoundLongitude')
    SubElement(eastBoundLongitude, 'gco:Decimal').text = str(my_resource.east_bounding)
    southBoundLatitude = SubElement(EX_GeographicBoundingBox, 'gmd:southBoundLatitude')
    SubElement(southBoundLatitude, 'gco:Decimal').text = str(my_resource.south_bounding)
    northBoundLatitude = SubElement(EX_GeographicBoundingBox, 'gmd:northBoundLatitude')
    SubElement(northBoundLatitude, 'gco:Decimal').text = str(my_resource.north_bounding)

    # supplemental information
    suppl_info = SupplemantInformation(my_resource)
    charstring(MD_DataIdentification, 'gmd:supplementalInformation', suppl_info.create_english_block(),
               suppl_info.create_french_block())

    distributionInfo = SubElement(root, 'gmd:distributionInfo')
    MD_Distribution = SubElement(distributionInfo, 'gmd:MD_Distribution')

    # distribution Format
    MD_Format = SubElement(SubElement(MD_Distribution, 'gmd:distributionFormat '), "gmd:MD_Format")
    charstring(MD_Format, 'gmd:name', my_resource.distribution_format)
    charstring(MD_Format, 'gmd:version', "n/a")

    # distributor
    distributor = SubElement(MD_Distribution, 'gmd:distributor')
    MD_Distributor = SubElement(distributor, 'gmd:MD_Distributor')
    distributorContact = SubElement(MD_Distributor, 'gmd:distributorContact')

    # for each point of contact
    for person in my_resource.resource_people.all():
        if person.role.id == 4:
            distributorContact.append(ci_responsible_party(person))

    # for each data resource
    for data_resource in my_resource.data_resources.all():
        transferOptions = SubElement(MD_Distribution, 'gmd:transferOptions')
        MD_DigitalTransferOptions = SubElement(transferOptions, 'gmd:MD_DigitalTransferOptions')
        onLine = SubElement(MD_DigitalTransferOptions, 'gmd:onLine')
        CI_OnlineResource = SubElement(onLine, 'gmd:CI_OnlineResource')
        linkage = SubElement(CI_OnlineResource, 'gmd:linkage')
        URL = SubElement(linkage, 'gmd:URL').text = data_resource.url
        charstring(CI_OnlineResource, 'gmd:protocol', data_resource.protocol)
        charstring(CI_OnlineResource, 'gmd:name', data_resource.name_eng, data_resource.name_fre)
        charstring(CI_OnlineResource, 'gmd:description', data_resource.content_type.english_value, data_resource.content_type.french_value)

    # for each web service
    for web_service in my_resource.web_services.all():
        transferOptions = SubElement(MD_Distribution, 'gmd:transferOptions')
        MD_DigitalTransferOptions = SubElement(transferOptions, 'gmd:MD_DigitalTransferOptions')
        onLine = SubElement(MD_DigitalTransferOptions, 'gmd:onLine', attrib={
            'xlink:role': web_service.service_language,
            })
        CI_OnlineResource = SubElement(onLine, 'gmd:CI_OnlineResource')
        linkage = SubElement(CI_OnlineResource, 'gmd:linkage')
        URL = SubElement(linkage, 'gmd:URL').text = web_service.url
        charstring(CI_OnlineResource, 'gmd:protocol', web_service.protocol)
        charstring(CI_OnlineResource, 'gmd:name', web_service.name_eng, web_service.name_fre)
        charstring(CI_OnlineResource, 'gmd:description', web_service.content_type.english_value,
                   web_service.content_type.french_value)

    my_xml = prettify(root)
    # my_xml = ""

    return my_xml


def verify(resource):
    checklist = Element('ul')

    # Has record been verified?
    if resource.certification_history.count() == 0:
        SubElement(checklist, "li").text = 'This record has not been certified'

    # if there is no point of contact it should be david
    if resource.resource_people.filter(role_id=4) == 0:
        SubElement(checklist, "li").text = "At least one point-of-contact is needed"

    # if there is no custodian it should added
    if resource.resource_people.filter(role_id=1) == 0:
        SubElement(checklist, "li").text = "At least one custodian is needed"

    for person in resource.people.all():

        # first check if there is an org present
        if person.organization == None:
            SubElement(checklist, 'li').text = "An organization is needed for {}".format(person)
        else:
            # do all contacts have org name in eng and fre?
            if person.organization.name_eng == None or person.organization.name_eng == "":
                SubElement(checklist, 'li').text = "An English organization name is needed for {}".format(person)
            if person.organization.name_fre == None or person.organization.name_fre == "":
                SubElement(checklist, 'li').text = "A French organization name is needed for {}".format(person)

            # check if there is an organization has a location
            if person.organization.location == None:
                SubElement(checklist,
                           'li').text = "A location is needed for '{}' which is the organization belonging to {}".format(
                    person.organization, person)
            else:
                # do all contacts have location in eng and fre?
                if person.organization.location.location_eng == None:
                    SubElement(checklist, 'li').text = "An English organization location is needed for {}".format(
                        person)
                if person.organization.location.location_fre == None:
                    SubElement(checklist, 'li').text = "A French organization location is needed for {}".format(person)

        # do all contacts have position name in eng and fre?
        if person.position_eng is None or person.position_eng == "":
            SubElement(checklist, 'li').text = "An English position name is needed for {}".format(person)
        if person.position_fre is None or person.position_fre == "":
            SubElement(checklist, 'li').text = "A French position name is needed for {}".format(person)

        # do all contacts have email?
        if person.user.email == None:
            SubElement(checklist, 'li').text = "An email address is needed for {}".format(person)

    # Title
    if resource.title_eng == None or resource.title_eng == "":
        SubElement(checklist, 'li').text = "English title missing"
    if resource.title_fre == None or resource.title_fre == "":
        SubElement(checklist, 'li').text = "French title missing"

    # description
    if resource.descr_eng == None or resource.descr_eng == "":
        SubElement(checklist, 'li').text = "English description missing"
    if resource.descr_fre == None or resource.descr_fre == "":
        SubElement(checklist, 'li').text = "French description missing"

    # purpose
    if resource.purpose_eng == None or resource.purpose_eng == "":
        SubElement(checklist, 'li').text = "English purpose missing"
    if resource.purpose_fre == None or resource.purpose_fre == "":
        SubElement(checklist, 'li').text = "French purpose missing"

    # file identifier
    if resource.uuid == None:
        SubElement(checklist, 'li').text = "file identifier (uuid) missing"

    # resource type
    if resource.resource_type_id == None:
        SubElement(checklist, 'li').text = "resource type missing"
    elif resource.resource_type.code == None:
        SubElement(checklist, 'li').text = "resource type code missing"

    # status
    if resource.status_id == None:
        SubElement(checklist, 'li').text = "status missing"
    elif resource.status.code == None:
        SubElement(checklist, 'li').text = "status code missing"

    # Spatial Reference System
    if resource.spat_ref_system_id == None:
        SubElement(checklist, 'li').text = "Spatial Reference System missing"
    elif resource.spat_ref_system.code == None:
        SubElement(checklist, 'li').text = "Spatial Reference System code missing"
    elif resource.spat_ref_system.codespace == None:
        SubElement(checklist, 'li').text = "Spatial Reference System codespace missing"

    # Spatial Representation Type
    if resource.spat_representation_id == None:
        SubElement(checklist, 'li').text = "Spatial Representation Type missing"
    elif resource.spat_representation.code == None:
        SubElement(checklist, 'li').text = "Spatial Representation Type code missing"

    # start time period
    if resource.time_start_year == None or resource.time_start_year == "":
        SubElement(checklist, 'li').text = "start time pertiod missing"

    # geographic description
    if resource.geo_descr_eng == None or resource.geo_descr_eng == "":
        SubElement(checklist, 'li').text = "English geographic description missing"
    if resource.geo_descr_fre == None or resource.geo_descr_fre == "":
        SubElement(checklist, 'li').text = "French geographic description missing"

    # west bound
    if resource.west_bounding == None or resource.west_bounding == "":
        SubElement(checklist, 'li').text = "west bounding coordinate missing"

    # south bound
    if resource.south_bounding == None or resource.south_bounding == "":
        SubElement(checklist, 'li').text = "south bounding coordinate missing"

    # east bound
    if resource.east_bounding == None or resource.east_bounding == "":
        SubElement(checklist, 'li').text = "east bounding coordinate missing"

    # north bound
    if resource.north_bounding == None or resource.north_bounding == "":
        SubElement(checklist, 'li').text = "north bounding coordinate missing"

    # distribution format
    if resource.distribution_format == None or resource.distribution_format == "":
        SubElement(checklist, 'li').text = "distribution format missing"

    # data character set
    if resource.data_char_set_id == None:
        SubElement(checklist, 'li').text = "data character set missing"
    elif resource.data_char_set.code == None:
        SubElement(checklist, 'li').text = "data character set code missing"

    # maintenance frequency
    if resource.maintenance_id == None:
        SubElement(checklist, 'li').text = "maintenance frequency missing"
    elif resource.maintenance.code == None:
        SubElement(checklist, 'li').text = "maintenance frequency code missing"

    # Are all keywords bilingual?
    ## examine all keywords, excluding ISO topic category which will be handled explicitly by FGP
    for keyword in resource.keywords.filter(~Q(keyword_domain_id=8)):
        if keyword.text_value_fre == None or keyword.text_value_fre == "":
            SubElement(checklist, 'li').text = 'French value for keyword is needed for <a href="{}">{}</a>'.format(
                reverse('inventory:keyword_detail', kwargs={'resource': resource.id, 'pk': keyword.id, }),
                keyword.text_value_eng
            )
        elif keyword.text_value_eng == None or keyword.text_value_eng == "":
            SubElement(checklist, 'li').text = "English value for keyword is needed for '{}'".format(
                keyword.text_value_fre)

    # DFO area?
    if resource.keywords.filter(keyword_domain_id=7).count() == 0:
        SubElement(checklist, 'li').text = "DFO area needed"

    # Topic category?
    if resource.keywords.filter(keyword_domain_id=8).count() == 0:
        SubElement(checklist, 'li').text = "Topic category needed"

    # CST?
    if resource.keywords.filter(keyword_domain_id=6).count() == 0:
        SubElement(checklist, 'li').text = "Core Subject needed"

    # security use limitation (techincally optional)
    if resource.security_use_limitation_eng == None or resource.security_use_limitation_eng == "":
        SubElement(checklist, 'li').text = "English security use limitation missing"
    if resource.security_use_limitation_fre == None or resource.security_use_limitation_fre == "":
        SubElement(checklist, 'li').text = "French security use limitation missing"

    # security classification (techincally optional)
    if resource.security_classification_id == None:
        SubElement(checklist, 'li').text = "security classification missing"
    elif resource.security_classification.code == None:
        SubElement(checklist, 'li').text = "security classification code missing"

    #  Checks on Optional fields #
    ##############################

    # QC process
    if (resource.qc_process_descr_eng != None and resource.qc_process_descr_fre == None) or (
            resource.qc_process_descr_eng == None and resource.qc_process_descr_fre != None):
        SubElement(checklist,
                   'li').text = "'QC Process description' is an optional field, but if entered, must be present in both languages"

    # Physical Sample Description
    if (resource.physical_sample_descr_eng != None and resource.physical_sample_descr_fre == None) or (
            resource.physical_sample_descr_eng == None and resource.physical_sample_descr_fre != None):
        SubElement(checklist,
                   'li').text = "'Physical Sample Description' is an optional field, but if entered, must be present in both languages"

    # Parameters Collected
    if (resource.parameters_collected_eng != None and resource.parameters_collected_fre == None) or (
            resource.parameters_collected_eng == None and resource.parameters_collected_fre != None):
        SubElement(checklist,
                   'li').text = "'Parameters Collected' is an optional field, but if entered, must be present in both languages"

    # Sampling Method
    if (resource.sampling_method_eng != None and resource.sampling_method_fre == None) or (
            resource.sampling_method_eng == None and resource.sampling_method_fre != None):
        SubElement(checklist,
                   'li').text = "'Sampling Method' is an optional field, but if entered, must be present in both languages"

    # Resource Constraints
    if (resource.resource_constraint_eng != None and resource.resource_constraint_fre == None) or (
            resource.resource_constraint_eng == None and resource.resource_constraint_fre != None):
        SubElement(checklist,
                   'li').text = "'Resource Constraints' is an optional field, but if entered, must be present in both languages"

    return str(ElementTree.tostring(checklist, 'utf-8')).replace("b'", '').replace("&gt;", ">").replace("&lt;",
                                                                                                        "<").replace(
        'b"', '')
