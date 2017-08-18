<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE xslt:stylesheet [
        <!ENTITY nbsp "&#160;">
                                <!ENTITY ensp "&#8194;">
        ]>
<xslt:stylesheet version="1.0"
                 xmlns:xslt="http://www.w3.org/1999/XSL/Transform"
                 xmlns:xns="http://www.w3.org/1999/xhtml"
                 xmlns:str="http://exslt.org/strings"
                 xmlns:exsl="http://exslt.org/common"
                 exclude-result-prefixes="xslt xns exsl str">
    <xslt:output omit-xml-declaration="yes" indent="yes"/>
    <xslt:strip-space elements="*"/>
    <xslt:variable name="vQ">"</xslt:variable>
    <xslt:variable name="lt"><xslt:text>&lt;</xslt:text></xslt:variable>
    <xslt:variable name="gt"><xslt:text>&gt;</xslt:text></xslt:variable>
  
    <xslt:template match="*">
        <!-- Readable List Form -->
        <!--<xslt:value-of select="concat('Element: ', name(), '&#xA;')"/>-->
        <!--<xslt:for-each select="@*">-->
            <!--<xslt:value-of select="concat(' - Attributes: ', name(), ' = ', $vQ, ., $vQ, '&#xA;')"/>-->
        <!--</xslt:for-each>-->
        <ClassnameContainer>
            <!-- Element List Form -->
            <xslt:element name="{name()}">
                <xslt:copy-of select="@*"/>
            </xslt:element>
            <xslt:apply-templates select="*">
                <!--This sort is affected by the parent nodes, so they will be sorted within each parent-->
                <xslt:sort select="name()" data-type="text"/>
            </xslt:apply-templates>
        </ClassnameContainer>
    </xslt:template>
    
    <!--<xslt:for-each select="exslt:node-set($all_nodes)">
        <xslt:sort select="name()" data-type="text"/>
        <xslt:copy-of select="."/>
    </xslt:for-each>-->
    
</xslt:stylesheet>
