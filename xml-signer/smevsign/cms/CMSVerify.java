/**
 * $RCSfile$
 * version $Revision$
 * created 16.08.2007 11:28:24 by kunina
 * last modified $Date$ by $Author$
 * (C) ООО Крипто-Про 2004-2007.
 *
 * modifyed by gosha20777 <gosha20777@live.ru>
 * (C) 2020
 */
package smevsign.cms;

import com.objsys.asn1j.runtime.*;
import ru.CryptoPro.JCP.ASN.CertificateExtensions.GeneralName;
import ru.CryptoPro.JCP.ASN.CertificateExtensions.GeneralNames;
import ru.CryptoPro.JCP.ASN.CryptographicMessageSyntax.*;
import ru.CryptoPro.JCP.ASN.PKIX1Explicit88.*;
import ru.CryptoPro.JCP.JCP;
import ru.CryptoPro.JCP.params.OID;
import ru.CryptoPro.JCP.tools.Array;

import java.security.Signature;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.util.Arrays;

/**
 * CMS Verify (поиск сертификатов: 1)CMS, 2)заданные сертификаты, 3)store(?))
 * [Проверка параллельных подписей  и подписей с signedAttributes]
 * <p/>
 * Проверяет:
 * <p/>
 * CMS_samples.CMSSign
 * <p/>
 * csptest -lowsign -in data.txt -my key -sign -out data_low.sgn -add
 * <p/>
 * csptest -lowsign -in data.txt -my key -sign -out data_low.sgn (нет вложенного
 * сертификата)
 * <p/>
 * csptest -sfsign -in data.txt -my key -sign -out data_sf.sgn -add
 * <p/>
 * csptest -sfsign -in data.txt -my key -sign -out data_sf.sgn (нет вложенного
 * сертификата)
 *
 * @author Copyright 2004-2009 Crypto-Pro. All rights reserved.
 * @.Version
 */
public class CMSVerify {

//CMS.java
private static final String CMS_FILE = "cms_data_sgn";
//CMSSign.java
//private static final String CMS_FILE = "cms_data_low_sgn";
//private static final String CMS_FILE = "cms_data_sf_sgn";

private static final String CMS_FILE_PATH =
    CMStools.TEST_PATH + CMStools.SEPAR + CMS_FILE + CMStools.CMS_EXT;

private static StringBuffer out = new StringBuffer("");
private static StringBuffer out1 = new StringBuffer("");
private static int validsign;

 /**/
private CMSVerify() {
    ;
}

public static void main(String[] args) throws Exception {

    //данные для проверки (CMS)
    final byte[] signdata = Array.readFile(CMS_FILE_PATH);
    //    final Certificate cert = CMStools.loadCertificate(CMStools.SIGN_KEY_NAME);
    //Certificate cert = CMStools.readCertificate(CMStools.SIGN_CERT_PATH);

    //проверка
    final Certificate[] certs = new Certificate[1];
    certs[0] = CMStools.loadCertificate(CMStools.SIGN_KEY_NAME);
    CMSVerify(signdata, certs, null);
}

/**
 * проверка CMS
 *
 * @param buffer буфер
 * @param certs сертификаты
 * @param data данные
 * @throws Exception e
 *
 * @deprecated начиная с версии 1.0.54, следует использовать функцонал CAdES API (CAdES.jar)
 */
public static void CMSVerify(byte[] buffer, Certificate[] certs,
    byte[] data) throws Exception {
    CMSVerifyEx(buffer, certs, data, CMStools.DIGEST_OID,
        CMStools.DIGEST_ALG_NAME, JCP.GOST_EL_SIGN_NAME,
        JCP.PROVIDER_NAME);
}

/**
 * проверка CMS
 *
 * @param buffer буфер
 * @param certs сертификаты
 * @param data данные
 * @param digestOidValue OID алгоритма хеширования
 * @param digestAlg алгоритм хеширования
 * @param signAlg алгоритм подписи
 * @param providerName имя провайдера
 * @throws Exception e
 *
 * @deprecated начиная с версии 1.0.54, следует использовать функцонал CAdES API (CAdES.jar)
 * @since 2.0
 */
public static void CMSVerifyEx(byte[] buffer, Certificate[] certs,
    byte[] data, String digestOidValue, String digestAlg,
    String signAlg, String providerName) throws Exception {

    //clear buffers fo logs
    out = new StringBuffer("");
    out1 = new StringBuffer("");

    final Asn1BerDecodeBuffer asnBuf = new Asn1BerDecodeBuffer(buffer);
    final ContentInfo all = new ContentInfo();
    all.decode(asnBuf);

    if (!new OID(CMStools.STR_CMS_OID_SIGNED).eq(all.contentType.value)) {
        throw new Exception("Not supported");
    } // if

    final SignedData cms = (SignedData) all.content;
    final byte[] text;

    if (cms.encapContentInfo.eContent != null) {
        text = cms.encapContentInfo.eContent.value;
    } // if
    else if (data != null) {
        text = data;
    } // else
    else {
        throw new Exception("No content for verify");
    } // else

    if(CMStools.logger != null) {
        CMStools.logger.info("Source data: " + new String(text));
    }

    OID digestOid = null;
    final DigestAlgorithmIdentifier digestAlgorithmIdentifier =
        new DigestAlgorithmIdentifier(new OID(digestOidValue).value);

    for (int i = 0; i < cms.digestAlgorithms.elements.length; i++) {
        if (cms.digestAlgorithms.elements[i].algorithm
            .equals(digestAlgorithmIdentifier.algorithm)) {
            digestOid = new OID(cms.digestAlgorithms.elements[i].algorithm.value);
            break;
        } // if
    } // for

    if (digestOid == null) {
        throw new Exception("Unknown digest");
    } // if

    final OID eContTypeOID = new OID(cms.encapContentInfo.eContentType.value);
    if (cms.certificates != null) {

        //Проверка на вложенных сертификатах
        if (CMStools.logger != null) {
            CMStools.logger.info("Validation on certificates founded in CMS.");
        }

        for (int i = 0; i < cms.certificates.elements.length; i++) {

            final Asn1BerEncodeBuffer encBuf = new Asn1BerEncodeBuffer();
            cms.certificates.elements[i].encode(encBuf);

            final CertificateFactory cf = CertificateFactory.getInstance("X.509");
            final X509Certificate cert = (X509Certificate) cf
                .generateCertificate(encBuf.getInputStream());

            for (int j = 0; j < cms.signerInfos.elements.length; j++) {

                final SignerInfo info = cms.signerInfos.elements[j];
                if (!digestOid.equals(new OID(info.digestAlgorithm.algorithm.value))) {
                    throw new Exception("Not signed on certificate.");
                } // if

                final boolean checkResult = verifyOnCert(cert,
                   cms.signerInfos.elements[j], text, eContTypeOID,
                    true, digestAlg, signAlg, providerName);

                writeLog(checkResult, j, i, cert);

            } // for

        } // for

    } // if
    else if (certs != null) {

        //Проверка на указанных сертификатах
        if (CMStools.logger != null) {
            CMStools.logger.info("Certificates for validation not found in CMS.\n" +
                    "Try verify on specified certificates...");
        }

        for (int i = 0; i < certs.length; i++) {

            final X509Certificate cert = (X509Certificate) certs[i];

            for (int j = 0; j < cms.signerInfos.elements.length; j++) {

                final SignerInfo info = cms.signerInfos.elements[j];

                if (!digestOid.equals(new OID(info.digestAlgorithm.algorithm.value))) {
                    throw new Exception("Not signed on certificate.");
                } // if

                final boolean checkResult = verifyOnCert(cert,
                    cms.signerInfos.elements[j], text, eContTypeOID,
                    true, digestAlg, signAlg, providerName);

                writeLog(checkResult, j, i, cert);

            } // for

        } // for

    } // else
    else {
        if (CMStools.logger != null) {
            CMStools.logger.warning("Certificates for validation not found");
        }
    } // else

    if (validsign == 0) {
        throw new Exception("Signatures are invalid" + out1);
    } // if

    if (cms.signerInfos.elements.length > validsign) {
        throw new Exception("Some signatures are invalid:" + out + out1);
    } // if
    else {
        if (CMStools.logger != null) {
            CMStools.logger.info("All signatures are valid:" + out);
        }
    } // else
}

/**
 * Попытка проверки подписи на указанном сертификате.
 * Проверка может быть выполнена как по отсортированным
 * подписанным аттрибутам, так и по несортированным.
 *
 * @param cert сертификат для проверки
 * @param text текст для проверки
 * @param info подпись
 * @param eContentTypeOID тип содержимого
 * @param needSortSignedAttributes True, если необходимо проверить
 * подпись по отсортированным подписанным аттрибутам. По умолчанию
 * подписанные аттрибуты сортируются перед кодированием.
 * @param digestAlg Алгоритм хеширования.
 * @param signAlg Алгоритм подписи.
 * @param providerName Имя провайдера.
 * @return верна ли подпись
 * @throws Exception ошибки
 */
private static boolean verifyOnCert(X509Certificate cert, SignerInfo info,
    byte[] text, OID eContentTypeOID, boolean needSortSignedAttributes,
    String digestAlg, String signAlg, String providerName)
    throws Exception {

    //подпись
    final byte[] sign = info.signature.value;

    //данные для проверки подписи
    final byte[] data;

    if (info.signedAttrs == null) {
        //аттрибуты подписи не присутствуют
        //данные для проверки подписи
        data = text;
    } // if
    else {

        //присутствуют аттрибуты подписи (SignedAttr)
        final Attribute[] signAttrElem = info.signedAttrs.elements;

        //проверка аттрибута signing-certificateV2
        final Asn1ObjectIdentifier signingCertificateV2Oid = new Asn1ObjectIdentifier(
            (new OID(ALL_PKIX1Explicit88Values.id_aa_signingCertificateV2)).value);
        Attribute signingCertificateV2Attr = null;

        for (int r = 0; r < signAttrElem.length; r++) {
            final Asn1ObjectIdentifier oid = signAttrElem[r].type;
            if (oid.equals(signingCertificateV2Oid)) {
                signingCertificateV2Attr = signAttrElem[r];
            } // if
        } // for

        if (signingCertificateV2Attr != null) {

            SigningCertificateV2 signingCertificateV2 = (SigningCertificateV2)
                signingCertificateV2Attr.values.elements[0];
            _SeqOfESSCertIDv2 essCertIDv2s = signingCertificateV2.certs;

            for (int s = 0; s < essCertIDv2s.elements.length; s++) {

                ESSCertIDv2 essCertIDv2 = essCertIDv2s.elements[s];

                CertHash expectedCertHash = essCertIDv2.certHash;
                AlgorithmIdentifier expectedHashAlgorithm = essCertIDv2.hashAlgorithm;

                IssuerSerial expectedIssuerSerial = essCertIDv2.issuerSerial;
                Asn1BerEncodeBuffer encodedExpectedIssuerSerial = new Asn1BerEncodeBuffer();
                expectedIssuerSerial.encode(encodedExpectedIssuerSerial);

                OID expectedHashAlgorithmOid = new OID(expectedHashAlgorithm.algorithm.value);
                CertHash actualCertHash = new CertHash(CMStools.digestm(cert.getEncoded(),
                    expectedHashAlgorithmOid.toString(), providerName));

                ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate certificate =
                    new ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate();
                Asn1BerDecodeBuffer decodeBuffer =
                    new Asn1BerDecodeBuffer(cert.getEncoded());
                certificate.decode(decodeBuffer);

                GeneralName[] issuerName = new GeneralName[1];
                issuerName[0] = new GeneralName(GeneralName._DIRECTORYNAME,
                    certificate.tbsCertificate.issuer);
                GeneralNames issuerNames = new GeneralNames(issuerName);

                IssuerSerial actualIssuerSerial = new IssuerSerial(issuerNames,
                    certificate.tbsCertificate.serialNumber);
                Asn1BerEncodeBuffer encodedActualIssuerSerial = new Asn1BerEncodeBuffer();
                actualIssuerSerial.encode(encodedActualIssuerSerial);

                if ( !(Arrays.equals(actualCertHash.value, expectedCertHash.value) &&
                     Arrays.equals(encodedActualIssuerSerial.getMsgCopy(),
                        encodedActualIssuerSerial.getMsgCopy())) ) {

                    System.out.println("Certificate stored in signing-certificateV2 " +
                        "is not equal to " + cert.getSubjectDN());
                    return false;
                } // if

            } // for

        } // if

        //проверка аттрибута content-type
        final Asn1ObjectIdentifier contentTypeOid = new Asn1ObjectIdentifier(
            (new OID(CMStools.STR_CMS_OID_CONT_TYP_ATTR)).value);
        Attribute contentTypeAttr = null;

        for (int r = 0; r < signAttrElem.length; r++) {
            final Asn1ObjectIdentifier oid = signAttrElem[r].type;
            if (oid.equals(contentTypeOid)) {
                contentTypeAttr = signAttrElem[r];
            } // if
        } // for

        if (contentTypeAttr == null) {
            throw new Exception("content-type attribute not present");
        } // if

        if (!contentTypeAttr.values.elements[0]
            .equals(new Asn1ObjectIdentifier(eContentTypeOID.value))) {
            throw new Exception("content-type attribute OID not equal eContentType OID");
        } // if

        //проверка аттрибута message-digest
        final Asn1ObjectIdentifier messageDigestOid = new Asn1ObjectIdentifier(
            (new OID(CMStools.STR_CMS_OID_DIGEST_ATTR)).value);

        Attribute messageDigestAttr = null;

        for (int r = 0; r < signAttrElem.length; r++) {
            final Asn1ObjectIdentifier oid = signAttrElem[r].type;
            if (oid.equals(messageDigestOid)) {
                messageDigestAttr = signAttrElem[r];
            } // if
        } // for

        if (messageDigestAttr == null) {
            throw new Exception("message-digest attribute not present");
        } // if

        final Asn1Type open = messageDigestAttr.values.elements[0];
        final Asn1OctetString hash = (Asn1OctetString) open;
        final byte[] md = hash.value;

        //вычисление messageDigest
        final byte[] dm = CMStools.digestm(text, digestAlg, providerName);

        if (!Array.toHexString(dm).equals(Array.toHexString(md))) {
            throw new Exception("message-digest attribute verify failed");
        } // if

        //проверка аттрибута signing-time
        final Asn1ObjectIdentifier signTimeOid = new Asn1ObjectIdentifier(
            (new OID(CMStools.STR_CMS_OID_SIGN_TYM_ATTR)).value);

        Attribute signTimeAttr = null;

        for (int r = 0; r < signAttrElem.length; r++) {
            final Asn1ObjectIdentifier oid = signAttrElem[r].type;
            if (oid.equals(signTimeOid)) {
                signTimeAttr = signAttrElem[r];
            } // if
        } // for

        if (signTimeAttr != null) {
            //проверка (необязательно)
            Time sigTime = (Time)signTimeAttr.values.elements[0];
            Asn1UTCTime time = (Asn1UTCTime) sigTime.getElement();
            System.out.println("Signing Time: " + time);
        } // if

        //данные для проверки подписи
        final Asn1BerEncodeBuffer encBufSignedAttr = new Asn1BerEncodeBuffer();
        info.signedAttrs.needSortSignedAttributes = needSortSignedAttributes;
        info.signedAttrs.encode(encBufSignedAttr);

        data = encBufSignedAttr.getMsgCopy();
    }

    // Проверяем подпись.
    Signature signature = Signature.getInstance(signAlg, providerName);
    signature.initVerify(cert);
    signature.update(data);

    boolean verified = signature.verify(sign);

    // Если подпись некорректна, но нас есть подписанные аттрибуты,
    // то пробуем проверить подпись также, отключив сортировку аттрибутов
    // перед кодированием в байтовый массив.
    if (!verified && info.signedAttrs != null && needSortSignedAttributes) {
        return verifyOnCert(cert, info, text, eContentTypeOID,
            false, digestAlg, signAlg, providerName);
    } // if

    return verified;
}

/**
 * write log
 *
 * @param checkResult прошла ли проверка
 * @param signNum номер подписи
 * @param certNum номер сертификата
 * @param cert сертификат
 */
private static void writeLog(boolean checkResult, int signNum,
    int certNum, X509Certificate cert) {
    if (checkResult) {
        out.append("\n");
        out.append("sign[");
        out.append(signNum);
        out.append("] - Valid signature on cert[");
        out.append(certNum);
        out.append("] (");
        out.append(cert.getSubjectX500Principal());
        out.append(")");
        validsign += 1;
    } // if
    else {
        out1.append("\n");
        out1.append("sign[");
        out1.append(signNum);
        out1.append("] - Invalid signature on cert[");
        out1.append(certNum);
        out1.append("] (");
        out1.append(cert.getSubjectX500Principal());
        out1.append(")");
    } // else
}
}
