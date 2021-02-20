/**
 * $RCSfile$
 * version $Revision$
 * created 16.08.2007 11:04:11 by kunina
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

import java.security.PrivateKey;
import java.security.Signature;
import java.security.cert.Certificate;
import java.security.cert.X509Certificate;
import java.util.Calendar;

/**
 * CMSSign n sign параллельные подписи с укладкой сертификатов
 * <p/>
 * проверяется:
 * <p/>
 * CMS_samples.CMSVerify
 * <p/>
 * csptest -sfsign -my key -verify -in data.sgn (без указания сертификата (-my)
 * csptest выдает ошибку приложения)
 * <p/>
 * csptest -lowsign -in data.sgn -verify (не проверяет //недостаточно
 * криптографических параметров//...-my не влияет)
 *
 * @author Copyright 2004-2009 Crypto-Pro. All rights reserved.
 * @.Version
 */
public class CMSSign {

/**
 * создать cms сообщение с подписью на хэш данных
 */
private static final boolean LOW_SIGN = true;
private static final String CMS_FILE_LOW = "cms_data_low_sgn";
private static final String CMS_FILE_LOW_PATH =
    CMStools.TEST_PATH + CMStools.SEPAR + CMS_FILE_LOW + CMStools.CMS_EXT;

/**
 * создать cms сообщение с подписью на хэш signedAttibutes
 */
private static final boolean SF_SIGN = true;
private static final String CMS_FILE_SF = "cms_data_sf_sgn";
private static final String CMS_FILE_SF_PATH =
    CMStools.TEST_PATH + CMStools.SEPAR + CMS_FILE_SF + CMStools.CMS_EXT;

/**
 * создать cms сообщение формата CAdES-BES с подписью на хэш signedAttibutes
 */
private static final boolean CAdES_BES_SIGN = true;
private static final String CMS_FILE_CAdES_BES = "cms_data_cades_bes_sgn";
private static final String CMS_FILE_CAdES_BES_PATH =
    CMStools.TEST_PATH + CMStools.SEPAR + CMS_FILE_CAdES_BES + CMStools.CMS_EXT;

 /**/
private CMSSign() {
    ;
}

/**
 * main Sign (+Verify)
 *
 * @throws Exception e
 */
public static void main(String[] args) throws Exception {

    //подготовка данных для запуска примера
    //CMStools.main(args);

    //read data or CMS
    final byte[] data = Array.readFile(CMStools.DATA_FILE_PATH);
    //    final byte[] data = Array.readFile(CMStools.CMS_FILE_LOW_PATH);
    //    final byte[] data = Array.readFile(CMStools.CMS_FILE_SF_PATH);

    //load keys for sign
    final PrivateKey[] keys = new PrivateKey[1];
    keys[0] = CMStools.loadKey(CMStools.SIGN_KEY_NAME,
            CMStools.SIGN_KEY_PASSWORD);
    //    keys[1] = CMStools.loadKey(CMStools.RECIP_KEY_NAME,
    //            CMStools.RECIP_KEY_PASSWORD);

    //load certificates
    final Certificate[] certs = new Certificate[1];
    certs[0] = CMStools.loadCertificate(CMStools.SIGN_KEY_NAME);
    //certs[1] = CMStools.loadCertificate(CMStools.RECIP_KEY_NAME);
    //        certs[0] = CMStools.readCertificate(CMStools.SIGN_KEY_NAME);
    //        //certs[1] = CMStools.readCertificate(CMStools.RECIP_KEY_NAME);

    //Sign (create CMS or sign CMS)
    boolean isCMS = true;
    final Asn1BerDecodeBuffer asnBuf = new Asn1BerDecodeBuffer(data);
    final ContentInfo all = new ContentInfo();

    try {
        all.decode(asnBuf);
    } catch (Exception e) {

        //создаем новое cms сообщение
        if (LOW_SIGN) {
            if (CMStools.logger != null) {
                CMStools.logger.info("Create CMS (low)");
            }
            createCMS(data, keys, certs, CMS_FILE_LOW_PATH, false);
        }

        if (SF_SIGN) {
            if (CMStools.logger != null) {
                CMStools.logger.info("Create CMS (sf)");
            }
            createHashCMS(data, keys, certs, CMS_FILE_SF_PATH, false);
        }

        // Создаем CAdES-BES подпись, имея хеш сообщения.
        if (CAdES_BES_SIGN) {
            if (CMStools.logger != null) {
                CMStools.logger.info("Create CAdES-BES CMS with digest of the data");
            }
            createHashCMSEx(CMStools.digestm(data, CMStools.DIGEST_ALG_NAME), true,
                keys, certs, CMS_FILE_CAdES_BES_PATH, true, true);
        } // if

        isCMS = false;
    }

    if (isCMS) {

        //подписываем уже созданное cms сообщение
        if (LOW_SIGN) {
            if (CMStools.logger != null) {
                CMStools.logger.info("Sign CMS (low)");
            }
            signCMS(data, keys, certs, CMS_FILE_LOW_PATH, null);
        }

        if (SF_SIGN) {
            if (CMStools.logger != null) {
                CMStools.logger.info("Sign CMS (sf)");
            }
            hashSignCMS(data, keys, certs, CMS_FILE_SF_PATH, null);
        }

    }

    //    //создание cms сообщения
    //    createCMS(data, keys, certs, CMS_FILE_LOW_PATH, false);
    //    createhashCMS(data, keys, certs, CMS_FILE_SF_PATH, false);
    //    //вторая подпись
    //    byte[] cmsdata = Array.readFile(CMS_FILE_LOW_PATH);
    //    signCMS(cmsdata, keys, certs, CMS_FILE_LOW_PATH, null);
    //    cmsdata = Array.readFile(CMS_FILE_SF_PATH);
    //    hashsignCMS(cmsdata, keys, certs, CMS_FILE_SF_PATH, null);
    //    //третья подпись
    //    cmsdata = Array.readFile(CMS_FILE_LOW_PATH);
    //    signCMS(cmsdata, keys, certs, CMS_FILE_LOW_PATH, null);
    //    cmsdata = Array.readFile(CMS_FILE_SF_PATH);
    //    hashsignCMS(cmsdata, keys, certs, CMS_FILE_SF_PATH, null);
    //    ...

    //Verify
    byte[] signdata = Array.readFile(CMS_FILE_LOW_PATH);
    if (CMStools.logger != null) {
        CMStools.logger.info("Verify created or signed CMS (LOW):");
    }
    CMSVerify.CMSVerify(signdata, certs, null);

    signdata = Array.readFile(CMS_FILE_SF_PATH);
    if (CMStools.logger != null) {
        CMStools.logger.info("Verify created or signed CMS (SF):");
    }
    CMSVerify.CMSVerify(signdata, certs, null);

    // Проверяем CAdES-BES подпись.
    signdata = Array.readFile(CMS_FILE_CAdES_BES_PATH);
    if (CMStools.logger != null) {
        CMStools.logger.info("Verify created CAdES-BES CMS:");
    }
    CMSVerify.CMSVerify(signdata, certs, data);
}

/**
 * Создание сообщения с подписью на хэш signedAttibutes
 *
 * @param data data
 * @param keys keys
 * @param certs certs
 * @param path path to write CMS
 * @param detached true if detached
 * @return byte[]
 * @throws Exception e
 */
public static byte[] createHashCMS(byte[] data, PrivateKey[] keys,
    Certificate[] certs, String path, boolean detached) throws Exception {
    return createHashCMSEx(data, false, keys, certs, path, detached, false);
}

/**
 * Создание сообщения с подписью на хэш signedAttibutes. Можно создать
 * подпись формата CAdES-BES (addSignCertV2=true) и по хешу сообщения, без
 * самого исходного сообщения (data - хеш сообщения, isExternalDigest=true
 * и detached=true).
 *
 * @param data data or digest
 * @param isExternalDigest True if data is a digest of the data
 * @param keys keys
 * @param certs certs
 * @param path path to write CMS
 * @param detached true if detached
 * @param addSignCertV2 add signingCertificateV2 (CAdES-BES)
 * @return byte[]
 * @throws Exception e
 */
public static byte[] createHashCMSEx(byte[] data, boolean isExternalDigest,
    PrivateKey[] keys, Certificate[] certs, String path, boolean detached,
    boolean addSignCertV2) throws Exception {
    return createHashCMSEx(data, isExternalDigest, keys, certs, path,
        detached, addSignCertV2, CMStools.DIGEST_OID_2012_256, CMStools.SIGN_OID_2012_256,
        CMStools.DIGEST_ALG_NAME_2012_256, JCP.GOST_SIGN_2012_256_NAME, JCP.PROVIDER_NAME);
}

/**
 * Создание сообщения с подписью на хэш signedAttibutes. Можно создать
 * подпись формата CAdES-BES (addSignCertV2=true) и по хешу сообщения, без
 * самого исходного сообщения (data - хеш сообщения, isExternalDigest=true
 * и detached=true).
 *
 * @param data data or digest
 * @param isExternalDigest True if data is a digest of the data
 * @param keys keys
 * @param certs certs
 * @param path path to write CMS
 * @param detached true if detached
 * @param addSignCertV2 add signingCertificateV2 (CAdES-BES)
 * @param digestOid digest algorithm OID
 * @param signOid signature algorithm OID
 * @param digestAlg digest algorithm name
 * @param signAlg signature algorithm name
 * @param providerName provider name
 * @return byte[]
 * @throws Exception e
 * @since 2.0
 */
public static byte[] createHashCMSEx(byte[] data, boolean isExternalDigest,
    PrivateKey[] keys, Certificate[] certs, String path, boolean detached,
    boolean addSignCertV2, String digestOid, String signOid, String digestAlg,
    String signAlg, String providerName) throws Exception {

    //create hashCMS
    final ContentInfo all = new ContentInfo();
    all.contentType = new Asn1ObjectIdentifier(
        new OID(CMStools.STR_CMS_OID_SIGNED).value);

    final SignedData cms = new SignedData();
    all.content = cms;
    cms.version = new CMSVersion(1);

    // digest
    cms.digestAlgorithms = new DigestAlgorithmIdentifiers(1);
    final DigestAlgorithmIdentifier a =
        new DigestAlgorithmIdentifier(new OID(digestOid).value);
    a.parameters = new Asn1Null();
    cms.digestAlgorithms.elements[0] = a;

    // Нельзя сделать подпись совмещенной, если нет данных, а
    // есть только хеш с них.
    if (isExternalDigest && !detached) {
        throw new Exception("Signature is attached but external " +
            "digest is available only (not data)");
    } // if

    if (detached) {
        cms.encapContentInfo = new EncapsulatedContentInfo(
            new Asn1ObjectIdentifier(
            new OID(CMStools.STR_CMS_OID_DATA).value), null);
    } // if
    else {
        cms.encapContentInfo =
            new EncapsulatedContentInfo(new Asn1ObjectIdentifier(
                new OID(CMStools.STR_CMS_OID_DATA).value),
                new Asn1OctetString(data));
    } // else

    // certificates
    final int nCerts = certs.length;
    cms.certificates = new CertificateSet(nCerts);
    cms.certificates.elements = new CertificateChoices[nCerts];

    for (int i = 0; i < cms.certificates.elements.length; i++) {

        final ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate certificate =
            new ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate();
        final Asn1BerDecodeBuffer decodeBuffer =
            new Asn1BerDecodeBuffer(certs[i].getEncoded());
        certificate.decode(decodeBuffer);

        cms.certificates.elements[i] = new CertificateChoices();
        cms.certificates.elements[i].set_certificate(certificate);
    }

    // Signature.getInstance
    final Signature signature = Signature.getInstance(signAlg, providerName);
    byte[] sign;

    // signer infos
    final int nsign = keys.length;
    cms.signerInfos = new SignerInfos(nsign);
    for (int i = 0; i < cms.signerInfos.elements.length; i++) {

        cms.signerInfos.elements[i] = new SignerInfo();
        cms.signerInfos.elements[i].version = new CMSVersion(1);
        cms.signerInfos.elements[i].sid = new SignerIdentifier();

        final byte[] encodedName = ((X509Certificate) certs[i])
            .getIssuerX500Principal().getEncoded();
        final Asn1BerDecodeBuffer nameBuf =
            new Asn1BerDecodeBuffer(encodedName);
        final Name name = new Name();
        name.decode(nameBuf);

        final CertificateSerialNumber num = new CertificateSerialNumber(
            ((X509Certificate) certs[i]).getSerialNumber());
        cms.signerInfos.elements[i].sid.set_issuerAndSerialNumber(
            new IssuerAndSerialNumber(name, num));
        cms.signerInfos.elements[i].digestAlgorithm =
            new DigestAlgorithmIdentifier(new OID(digestOid).value);
        cms.signerInfos.elements[i].digestAlgorithm.parameters = new Asn1Null();
        cms.signerInfos.elements[i].signatureAlgorithm =
            new SignatureAlgorithmIdentifier(new OID(signOid).value);
        cms.signerInfos.elements[i].signatureAlgorithm.parameters =
            new Asn1Null();

        //signedAttributes
        final int kmax = addSignCertV2 ? 4 : 3;
        cms.signerInfos.elements[i].signedAttrs = new SignedAttributes(kmax);

        //-contentType
        int k = 0;
        cms.signerInfos.elements[i].signedAttrs.elements[k] =
            new Attribute(new OID(CMStools.STR_CMS_OID_CONT_TYP_ATTR).value,
            new Attribute_values(1));

        final Asn1Type conttype = new Asn1ObjectIdentifier(
            new OID(CMStools.STR_CMS_OID_DATA).value);

        cms.signerInfos.elements[i].signedAttrs.elements[k]
            .values.elements[0] = conttype;

        //-Time
        k += 1;
        cms.signerInfos.elements[i].signedAttrs.elements[k] =
            new Attribute(new OID(CMStools.STR_CMS_OID_SIGN_TYM_ATTR).value,
            new Attribute_values(1));

        final Time time = new Time();
        //        final Asn1GeneralizedTime genTime = new Asn1GeneralizedTime();
        //        //текущая дата с календаря
        //        genTime.setTime(Calendar.getInstance());
        //        time.set_generalTime(genTime);

        final Asn1UTCTime UTCTime = new Asn1UTCTime();
        //текущая дата с календаря
        UTCTime.setTime(Calendar.getInstance());
        time.set_utcTime(UTCTime);

        cms.signerInfos.elements[i].signedAttrs.elements[k].values.elements[0] =
            time.getElement();

        //-message digest
        k += 1;
        cms.signerInfos.elements[i].signedAttrs.elements[k] =
            new Attribute(new OID(CMStools.STR_CMS_OID_DIGEST_ATTR).value,
            new Attribute_values(1));

        final byte[] messageDigestBlob;

        // Если вместо данных у нас хеш, то сразу его передаем, ничего не вычисляем.
        if (isExternalDigest) {
            messageDigestBlob = data;
        } // if
        else {
            if (detached) {
                messageDigestBlob = CMStools.digestm(data, digestAlg, providerName);
            } // if
            else {
                messageDigestBlob = CMStools.digestm(cms.encapContentInfo.eContent.value,
                    digestAlg, providerName);
            } // else
        } // else

        final Asn1Type messageDigest = new Asn1OctetString(messageDigestBlob);

        cms.signerInfos.elements[i].signedAttrs.elements[k]
            .values.elements[0] = messageDigest;

        // Добавление signingCertificateV2 в подписанные аттрибуты, чтобы подпись
        // стала похожа на CAdES-BES.
        if (addSignCertV2) {

            // Собственно, аттрибут с OID'ом id_aa_signingCertificateV2.
            k += 1;
            cms.signerInfos.elements[i].signedAttrs.elements[k] =
                new Attribute(new OID(ALL_PKIX1Explicit88Values.id_aa_signingCertificateV2).value,
                new Attribute_values(1));

            // Идентификатор алгоритма хеширования, который использовался для
            // хеширования контекста сертификата ключа подписи.
            final DigestAlgorithmIdentifier digestAlgorithmIdentifier =
                new DigestAlgorithmIdentifier(new OID(digestOid).value);

            // Хеш сертификата ключа подписи.
            final CertHash certHash = new CertHash(
                CMStools.digestm(certs[i].getEncoded(), digestAlg, providerName));

            // Issuer name из сертификата ключа подписи.
            GeneralName generalName = new GeneralName();
            generalName.set_directoryName(name);

            GeneralNames generalNames = new GeneralNames();
            generalNames.elements = new GeneralName[1];
            generalNames.elements[0] = generalName;

            // Комбинируем издателя и серийный номер.
            IssuerSerial issuerSerial = new IssuerSerial(generalNames, num);

            ESSCertIDv2 essCertIDv2 =
                new ESSCertIDv2(digestAlgorithmIdentifier, certHash, issuerSerial);

            _SeqOfESSCertIDv2 essCertIDv2s = new _SeqOfESSCertIDv2(1);
            essCertIDv2s.elements = new ESSCertIDv2[1];
            essCertIDv2s.elements[0] = essCertIDv2;

            // Добавляем сам аттрибут.
            SigningCertificateV2 signingCertificateV2 = new SigningCertificateV2(essCertIDv2s);
            cms.signerInfos.elements[i].signedAttrs.elements[k].values.elements[0] = signingCertificateV2;

        } // if

        //signature
        Asn1BerEncodeBuffer encBufSignedAttr = new Asn1BerEncodeBuffer();
        cms.signerInfos.elements[i].signedAttrs
                .encode(encBufSignedAttr);
        final byte[] hsign = encBufSignedAttr.getMsgCopy();
        signature.initSign(keys[i]);
        signature.update(hsign);
        sign = signature.sign();

        cms.signerInfos.elements[i].signature = new SignatureValue(sign);
    }

    // encode
    final Asn1BerEncodeBuffer asnBuf = new Asn1BerEncodeBuffer();
    all.encode(asnBuf, true);
    if (path != null) {
        Array.writeFile(path, asnBuf.getMsgCopy());
    }
    return asnBuf.getMsgCopy();

}

/**
 * Создание сообщение с подписью на хэш данных
 *
 * @param data data
 * @param certs certs[]
 * @param keys keys
 * @param path path to write CMS
 * @param detached true if detached
 * @return byte[]
 * @throws Exception e
 */
public static byte[] createCMS(byte[] data, PrivateKey[] keys,
    Certificate[] certs, String path, boolean detached)
    throws Exception {
    return createCMSEx(data, keys, certs, path, detached,
        CMStools.DIGEST_OID, CMStools.SIGN_OID, JCP.GOST_EL_SIGN_NAME,
        JCP.PROVIDER_NAME);
}

/**
 * Создание сообщение с подписью на хэш данных
 *
 * @param data data
 * @param certs certs[]
 * @param keys keys
 * @param path path to write CMS
 * @param detached true if detached
 * @param digestOid digest algorithm OID
 * @param signOid signature algorithm OID
 * @param signAlg signature algorithm name
 * @param providerName provider name
 * @return byte[]
 * @throws Exception e
 * @since 2.0
 */
public static byte[] createCMSEx(byte[] data, PrivateKey[] keys,
    Certificate[] certs, String path, boolean detached, String digestOid,
    String signOid, String signAlg, String providerName) throws Exception {

    //create CMS
    final ContentInfo all = new ContentInfo();
    all.contentType = new Asn1ObjectIdentifier(
        new OID(CMStools.STR_CMS_OID_SIGNED).value);

    final SignedData cms = new SignedData();
    all.content = cms;
    cms.version = new CMSVersion(1);

    // digest
    cms.digestAlgorithms = new DigestAlgorithmIdentifiers(1);
    final DigestAlgorithmIdentifier a = new DigestAlgorithmIdentifier(
        new OID(digestOid).value);
    a.parameters = new Asn1Null();
    cms.digestAlgorithms.elements[0] = a;

    if (detached) {
        cms.encapContentInfo = new EncapsulatedContentInfo(
            new Asn1ObjectIdentifier(
            new OID(CMStools.STR_CMS_OID_DATA).value), null);
    } // if
    else {
        cms.encapContentInfo =
            new EncapsulatedContentInfo(new Asn1ObjectIdentifier(
                new OID(CMStools.STR_CMS_OID_DATA).value),
                new Asn1OctetString(data));
    } // else

    // certificates
    final int nCerts = certs.length;
    cms.certificates = new CertificateSet(nCerts);
    cms.certificates.elements = new CertificateChoices[nCerts];

    for (int i = 0; i < cms.certificates.elements.length; i++) {

        final ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate certificate =
            new ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate();
        final Asn1BerDecodeBuffer decodeBuffer =
            new Asn1BerDecodeBuffer(certs[i].getEncoded());
        certificate.decode(decodeBuffer);

        cms.certificates.elements[i] = new CertificateChoices();
        cms.certificates.elements[i].set_certificate(certificate);

    } // for

    // Signature.getInstance
    final Signature signature = Signature.getInstance(signAlg, providerName);
    byte[] sign;

    // signer infos
    final int nSign = keys.length;
    cms.signerInfos = new SignerInfos(nSign);
    for (int i = 0; i < cms.signerInfos.elements.length; i++) {

        signature.initSign(keys[i]);
        signature.update(data);
        sign = signature.sign();

        cms.signerInfos.elements[i] = new SignerInfo();
        cms.signerInfos.elements[i].version = new CMSVersion(1);
        cms.signerInfos.elements[i].sid = new SignerIdentifier();

        final byte[] encodedName = ((X509Certificate) certs[i])
            .getIssuerX500Principal().getEncoded();
        final Asn1BerDecodeBuffer nameBuf = new Asn1BerDecodeBuffer(encodedName);
        final Name name = new Name();
        name.decode(nameBuf);

        final CertificateSerialNumber num = new CertificateSerialNumber(
            ((X509Certificate) certs[i]).getSerialNumber());
        cms.signerInfos.elements[i].sid.set_issuerAndSerialNumber(
            new IssuerAndSerialNumber(name, num));
        cms.signerInfos.elements[i].digestAlgorithm =
            new DigestAlgorithmIdentifier(new OID(digestOid).value);
        cms.signerInfos.elements[i].digestAlgorithm.parameters = new Asn1Null();
        cms.signerInfos.elements[i].signatureAlgorithm =
            new SignatureAlgorithmIdentifier(new OID(signOid).value);
        cms.signerInfos.elements[i].signatureAlgorithm.parameters =
            new Asn1Null();
        cms.signerInfos.elements[i].signature = new SignatureValue(sign);
    }

    // encode
    final Asn1BerEncodeBuffer asnBuf = new Asn1BerEncodeBuffer();
    all.encode(asnBuf, true);
    if (path != null) {
        Array.writeFile(path, asnBuf.getMsgCopy());
    }
    return asnBuf.getMsgCopy();
}

/**
 * Подпись существующего сообщения (CMS) //хэш на данные
 *
 * @param buffer CMS
 * @param keys keys
 * @param certs certs
 * @param path path to write signCMS
 * @param data data if detached signature
 * @return byte[]
 * @throws Exception e
 */
public static byte[] signCMS(byte[] buffer, PrivateKey[] keys,
    Certificate[] certs, String path, byte[] data) throws Exception {
    return signCMSEx(buffer, keys, certs, path, data, CMStools.DIGEST_OID,
        CMStools.SIGN_OID, JCP.GOST_EL_SIGN_NAME, JCP.PROVIDER_NAME);
}

/**
 * Подпись существующего сообщения (CMS) //хэш на данные
 *
 * @param buffer CMS
 * @param keys keys
 * @param certs certs
 * @param path path to write signCMS
 * @param data data if detached signature
 * @param digestOidValue digest algorithm OID
 * @param signOidValue signature algorithm OID
 * @param signAlg signature algorithm name
 * @param providerName provider name
 * @return byte[]
 * @throws Exception e
 * @since 2.0
 */
public static byte[] signCMSEx(byte[] buffer, PrivateKey[] keys,
    Certificate[] certs, String path, byte[] data, String digestOidValue,
    String signOidValue, String signAlg, String providerName)
    throws Exception {

    int i;
    final Asn1BerDecodeBuffer asnBuf = new Asn1BerDecodeBuffer(buffer);
    final ContentInfo all = new ContentInfo();
    all.decode(asnBuf);

    if (!new OID(CMStools.STR_CMS_OID_SIGNED).eq(all.contentType.value)) {
        throw new Exception("Not supported");
    } // if

    final SignedData cms = (SignedData) all.content;
    if (cms.version.value != 1) {
        throw new Exception("Incorrect version");
    } // if

    if (!new OID(CMStools.STR_CMS_OID_DATA)
        .eq(cms.encapContentInfo.eContentType.value)) {
        throw new Exception("Nested not supported");
    } // if

    final byte[] text;
    if (cms.encapContentInfo.eContent != null) {
        text = cms.encapContentInfo.eContent.value;
    } // if
    else if (data != null) {
        text = data;
    } // else
    else {
        throw new Exception("No content");
    } // else

    //    final byte[] text = cms.encapContentInfo.eContent.value;
    OID digestOid = null;
    final DigestAlgorithmIdentifier a = new DigestAlgorithmIdentifier(
        new OID(digestOidValue).value);

    for (i = 0; i < cms.digestAlgorithms.elements.length; i++) {
        if (cms.digestAlgorithms.elements[i].algorithm.equals(a.algorithm)) {
            digestOid = new OID(cms.digestAlgorithms.elements[i].algorithm.value);
            break;
        } // if
    } // for

    if (digestOid == null) {
        throw new Exception("Unknown digest");
    } // if

    // certificates
    final CertificateChoices[] choices =
        new CertificateChoices[cms.certificates.elements.length];
    for (i = 0; i < cms.certificates.elements.length; i++) {
        choices[i] = cms.certificates.elements[i];
    }  // for

    final int nCerts = certs.length + choices.length;
    cms.certificates = new CertificateSet(nCerts);
    cms.certificates.elements = new CertificateChoices[nCerts];
    for (i = 0; i < choices.length; i++) {
        cms.certificates.elements[i] = choices[i];
    } // for

    for (i = 0; i < cms.certificates.elements.length - choices.length; i++) {

        final ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate certificate =
            new ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate();
        final Asn1BerDecodeBuffer decodeBuffer =
            new Asn1BerDecodeBuffer(certs[i].getEncoded());
        certificate.decode(decodeBuffer);
        cms.certificates.elements[i + choices.length] =
            new CertificateChoices();
        cms.certificates.elements[i + choices.length]
            .set_certificate(certificate);

    } // for

    // Signature.getInstance
    final Signature signature = Signature.getInstance(signAlg, providerName);
    byte[] sign;

    // signer infos
    final SignerInfo[] infos = new SignerInfo[cms.signerInfos.elements.length];
    for (i = 0; i < cms.signerInfos.elements.length; i++) {
        infos[i] = cms.signerInfos.elements[i];
    } // for

    final int nsign = keys.length + infos.length;
    cms.signerInfos = new SignerInfos(nsign);
    for (i = 0; i < infos.length; i++) {
        cms.signerInfos.elements[i] = infos[i];
    } // for

    for (i = 0; i < cms.signerInfos.elements.length - infos.length; i++) {

        signature.initSign(keys[i]);
        signature.update(text);
        sign = signature.sign();

        cms.signerInfos.elements[i + infos.length] = new SignerInfo();
        cms.signerInfos.elements[i + infos.length].version = new CMSVersion(1);
        cms.signerInfos.elements[i + infos.length].sid = new SignerIdentifier();

        final byte[] encodedName = ((X509Certificate) certs[i])
            .getIssuerX500Principal().getEncoded();

        final Asn1BerDecodeBuffer nameBuf = new Asn1BerDecodeBuffer(encodedName);
        final Name name = new Name();
        name.decode(nameBuf);

        final CertificateSerialNumber num = new CertificateSerialNumber(
            ((X509Certificate) certs[i]).getSerialNumber());
        cms.signerInfos.elements[i + infos.length].sid
            .set_issuerAndSerialNumber(
            new IssuerAndSerialNumber(name, num));
        cms.signerInfos.elements[i + infos.length].digestAlgorithm =
            new DigestAlgorithmIdentifier(new OID(digestOidValue).value);
        cms.signerInfos.elements[i + infos.length].digestAlgorithm.parameters =
            new Asn1Null();
        cms.signerInfos.elements[i + infos.length].signatureAlgorithm =
            new SignatureAlgorithmIdentifier(new OID(signOidValue).value);
        cms.signerInfos.elements[i + infos
            .length].signatureAlgorithm.parameters = new Asn1Null();
        cms.signerInfos.elements[i + infos.length].signature =
            new SignatureValue(sign);
    }

    // encode
    final Asn1BerEncodeBuffer asn1Buf = new Asn1BerEncodeBuffer();
    all.encode(asn1Buf, true);
    if (path != null) {
        Array.writeFile(path, asn1Buf.getMsgCopy());
    }
    return asn1Buf.getMsgCopy();
}

/**
 * Подпись существующего сообщения (CMS) //хэш на signedAttributes
 *
 * @param buffer CMS
 * @param keys keys
 * @param certs certs
 * @param path path to write signCMS
 * @param data data if detached signature
 * @return byte[]
 * @throws Exception e
 */
public static byte[] hashSignCMS(byte[] buffer, PrivateKey[] keys,
    Certificate[] certs, String path, byte[] data) throws Exception {
    return hashSignCMSEx(buffer, keys, certs, path, data, CMStools.DIGEST_OID,
        CMStools.SIGN_OID, CMStools.DIGEST_ALG_NAME, JCP.GOST_EL_SIGN_NAME,
        JCP.PROVIDER_NAME);
}

/**
 * Подпись существующего сообщения (CMS) //хэш на signedAttributes
 *
 * @param buffer CMS
 * @param keys keys
 * @param certs certs
 * @param path path to write signCMS
 * @param data data if detached signature
 * @param digestOidValue digest algorithm OID
 * @param signOidValue signature algorithm OID
 * @param digestAlg digest algorithm name
 * @param signAlg signature algorithm name
 * @param providerName provider name
 * @return byte[]
 * @throws Exception e
 * @since 2.0
 */
public static byte[] hashSignCMSEx(byte[] buffer, PrivateKey[] keys,
    Certificate[] certs, String path, byte[] data, String digestOidValue,
    String signOidValue, String digestAlg, String signAlg, String providerName)
    throws Exception {

    int i;
    final Asn1BerDecodeBuffer asnBuf = new Asn1BerDecodeBuffer(buffer);
    final ContentInfo all = new ContentInfo();
    all.decode(asnBuf);

    if (!new OID(CMStools.STR_CMS_OID_SIGNED).eq(all.contentType.value)) {
        throw new Exception("Not supported");
    } // if

    final SignedData cms = (SignedData) all.content;
    if (cms.version.value != 1) {
        throw new Exception("Incorrect version");
    } // if

    if (!new OID(CMStools.STR_CMS_OID_DATA)
        .eq(cms.encapContentInfo.eContentType.value)) {
        throw new Exception("Nested not supported");
    } // if

    OID digestOid = null;
    final DigestAlgorithmIdentifier a = new DigestAlgorithmIdentifier(
        new OID(digestOidValue).value);
    for (i = 0; i < cms.digestAlgorithms.elements.length; i++) {
        if (cms.digestAlgorithms.elements[i].algorithm.equals(a.algorithm)) {
            digestOid = new OID(cms.digestAlgorithms.elements[i].algorithm.value);
            break;
        } // if
    } // for

    if (digestOid == null) {
        throw new Exception("Unknown digest");
    } // if

    // certificates
    final CertificateChoices[] choices =
        new CertificateChoices[cms.certificates.elements.length];
    for (i = 0; i < cms.certificates.elements.length; i++) {
        choices[i] = cms.certificates.elements[i];
    } // for

    final int nCerts = certs.length + choices.length;
    cms.certificates = new CertificateSet(nCerts);
    cms.certificates.elements = new CertificateChoices[nCerts];
    for (i = 0; i < choices.length; i++) {
        cms.certificates.elements[i] = choices[i];
    } // for

    for (i = 0; i < cms.certificates.elements.length - choices.length; i++) {

        final ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate certificate =
            new ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Certificate();
        final Asn1BerDecodeBuffer decodeBuffer =
            new Asn1BerDecodeBuffer(certs[i].getEncoded());
        certificate.decode(decodeBuffer);

        cms.certificates.elements[i + choices.length] =
            new CertificateChoices();
        cms.certificates.elements[i + choices.length]
            .set_certificate(certificate);

    } // for

    // Signature.getInstance
    final Signature signature = Signature.getInstance(signAlg, providerName);
    byte[] sign;

    // signer infos
    final SignerInfo[] infos = new SignerInfo[cms.signerInfos.elements.length];
    for (i = 0; i < cms.signerInfos.elements.length; i++) {
        infos[i] = cms.signerInfos.elements[i];
    } // for

    final int nSign = keys.length + infos.length;
    cms.signerInfos = new SignerInfos(nSign);
    for (i = 0; i < infos.length; i++) {
        cms.signerInfos.elements[i] = infos[i];
    } // for

    for (i = 0; i < cms.signerInfos.elements.length - infos.length; i++) {

        cms.signerInfos.elements[i + infos.length] = new SignerInfo();
        cms.signerInfos.elements[i + infos.length].version = new CMSVersion(1);
        cms.signerInfos.elements[i + infos.length].sid = new SignerIdentifier();

        final byte[] encodedName = ((X509Certificate) certs[i])
            .getIssuerX500Principal().getEncoded();

        final Asn1BerDecodeBuffer nameBuf = new Asn1BerDecodeBuffer(encodedName);
        final Name name = new Name();
        name.decode(nameBuf);

        final CertificateSerialNumber num = new CertificateSerialNumber(
            ((X509Certificate) certs[i]).getSerialNumber());
        cms.signerInfos.elements[i + infos.length].sid
            .set_issuerAndSerialNumber(new IssuerAndSerialNumber(name, num));
        cms.signerInfos.elements[i + infos.length].digestAlgorithm =
            new DigestAlgorithmIdentifier(new OID(digestOidValue).value);
        cms.signerInfos.elements[i + infos.length].digestAlgorithm.parameters =
            new Asn1Null();
        cms.signerInfos.elements[i + infos.length].signatureAlgorithm =
            new SignatureAlgorithmIdentifier(new OID(signOidValue).value);
        cms.signerInfos.elements[i + infos
            .length].signatureAlgorithm.parameters = new Asn1Null();

        //signedAttributes
        final int kmax = 3;
        cms.signerInfos.elements[i + infos.length].signedAttrs =
            new SignedAttributes(kmax);

        //-contentType
        int k = 0;
        cms.signerInfos.elements[i + infos.length].signedAttrs.elements[k] =
            new Attribute(new OID(CMStools.STR_CMS_OID_CONT_TYP_ATTR).value,
            new Attribute_values(1));

        final Asn1Type conttype = new Asn1ObjectIdentifier(
            new OID(CMStools.STR_CMS_OID_DATA).value);

        cms.signerInfos.elements[i + infos
            .length].signedAttrs.elements[k].values.elements[0] =
            conttype;

        //-Time
        k += 1;
        cms.signerInfos.elements[i + infos.length].signedAttrs.elements[k] =
            new Attribute(new OID(CMStools.STR_CMS_OID_SIGN_TYM_ATTR).value,
            new Attribute_values(1));

        final Time time = new Time();
        //        final Asn1GeneralizedTime genTime = new Asn1GeneralizedTime();
        //        //текущая дата с календаря
        //        genTime.setTime(Calendar.getInstance());
        //        time.set_generalTime(genTime);

        final Asn1UTCTime UTCTime = new Asn1UTCTime();
        //текущая дата с календаря
        UTCTime.setTime(Calendar.getInstance());
        time.set_utcTime(UTCTime);

        cms.signerInfos.elements[i + infos
            .length].signedAttrs.elements[k].values.elements[0] =
            time.getElement();

        //-message digest
        k += 1;
        cms.signerInfos.elements[i + infos.length].signedAttrs.elements[k] =
            new Attribute(new OID(CMStools.STR_CMS_OID_DIGEST_ATTR).value,
            new Attribute_values(1));

        final byte[] messageDigestBlob;
        if (cms.encapContentInfo.eContent.value != null) {
            messageDigestBlob =  CMStools.digestm(
                cms.encapContentInfo.eContent.value, digestAlg, providerName);
        } // if
        else if (data != null) {
            messageDigestBlob = CMStools.digestm(data, digestAlg, providerName);
        } // else
        else {
            throw new Exception("No content");
        } // else

        final Asn1Type messageDigest = new Asn1OctetString(messageDigestBlob);

        cms.signerInfos.elements[i + infos
            .length].signedAttrs.elements[k].values.elements[0] =
            messageDigest;

        //signature
        Asn1BerEncodeBuffer encBufSignedAttr = new Asn1BerEncodeBuffer();
        cms.signerInfos.elements[i + infos.length].signedAttrs
            .encode(encBufSignedAttr);

        final byte[] hSign = encBufSignedAttr.getMsgCopy();
        signature.initSign(keys[i]);
        signature.update(hSign);
        sign = signature.sign();

        cms.signerInfos.elements[i + infos.length].signature =
            new SignatureValue(sign);
    }

    // encode
    final Asn1BerEncodeBuffer asn1Buf = new Asn1BerEncodeBuffer();
    all.encode(asn1Buf, true);
    if (path != null) {
        Array.writeFile(path, asn1Buf.getMsgCopy());
    }
    return asn1Buf.getMsgCopy();
}
}
