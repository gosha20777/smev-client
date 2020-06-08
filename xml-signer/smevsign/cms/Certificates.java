/**
 * created 27.05.2009 18:45:02 by kunina
 * last modified $Date$ by $Author$
 * (C) ООО Крипто-Про 2004-2009.
 *
 * modifyed by gosha20777 <gosha20777@live.ru>
 * (C) 2020
 */
package smevsign.cms;

import com.objsys.asn1j.runtime.*;
import org.bouncycastle.asn1.ASN1OctetString;
import ru.CryptoPro.JCP.ASN.CertificateExtensions.ALL_CertificateExtensionsValues;
import ru.CryptoPro.JCP.ASN.CertificateExtensions.BasicConstraintsSyntax;
import ru.CryptoPro.JCP.ASN.PKIX1Explicit88.Extension;
import ru.CryptoPro.JCP.JCP;
import ru.CryptoPro.JCPRequest.GostCertificateRequest;

import java.io.*;
import java.security.KeyPair;
import java.security.KeyStore;
import java.security.cert.*;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Примеры работы с сертификатами.
 *
 * @author Copyright 2004-2009 Crypto-Pro. All rights reserved.
 * @.Version
 */
public class Certificates {
/**
 * уникальное имя записываемого сертификата
 */
private static final String ALIAS_2001 = "newCert_2001";
/**
* уникальное имя записываемого сертификата
*/
private static final String ALIAS_2012_256 = "newCert_2012_256";
/**
 * уникальное имя записываемого сертификата
 */
private static final String ALIAS_2012_512 = "newCert_2012_512";
/**
 * имя субъекта для генерирования запроса на сертификат
 */
private static final String DNAME_2001 = "CN=" + ALIAS_2001 + ", O=CryptoPro, C=RU";
/**
 * имя субъекта для генерирования запроса на сертификат
 */
private static final String DNAME_2012_256 = "CN=" + ALIAS_2012_256 + ", O=CryptoPro, C=RU";
/**
 * имя субъекта для генерирования запроса на сертификат
 */
private static final String DNAME_2012_512 = "CN=" + ALIAS_2012_512 + ", O=CryptoPro, C=RU";
/**
 * http-адрес центра центра сертификации
 */
public static final String HTTP_ADDRESS = "http://www.cryptopro.ru/certsrv/";
/**
 * имя ключевого носителя для инициализации хранилища
 */
private static final String STORE_TYPE = Constants.KEYSTORE_TYPE;
/**
 * алгоритм ключа (ГОСТ Р 34.10-2001)
 */
private static final String KEY_ALG_2001 = Constants.SIGN_KEY_PAIR_ALG_2001;
/**
 * алгоритм ключа (ГОСТ Р 34.10-2012, 256)
 */
private static final String KEY_ALG_2012_256 = Constants.SIGN_KEY_PAIR_ALG_2012_256;
/**
 * алгоритм ключа (ГОСТ Р 34.10-2012, 512)
 */
private static final String KEY_ALG_2012_512 = Constants.SIGN_KEY_PAIR_ALG_2012_512;
/**
 * устанавливаемый пароль на хранилище сертификатов
 */
private static final char[] STORE_PASS = "password".toCharArray();
/**
 * путь к файлу хранилища сертификатов
 */
private static final String STORE_PATH_2001 =
        System.getProperty("user.home") + File.separator + "new_2001.keystore";
/**
 * путь к файлу хранилища сертификатов
 */
private static final String STORE_PATH_2012_256 =
        System.getProperty("user.home") + File.separator + "new_2012_256.keystore";
/**
 * путь к файлу хранилища сертификатов
 */
private static final String STORE_PATH_2012_512 =
        System.getProperty("user.home") + File.separator + "new_2012_512.keystore";
/**
 * путь для записи сертификата
 */
private static final String CERT_PATH_2001 =
        System.getProperty("user.home") + File.separator + "newCertificate_2001.cer";
/**
 * путь для записи сертификата
 */
private static final String CERT_PATH_2012_256 =
        System.getProperty("user.home") + File.separator + "newCertificate_2012_256.cer";
/**
 * путь для записи сертификата
 */
private static final String CERT_PATH_2012_512 =
        System.getProperty("user.home") + File.separator + "newCertificate_2012_512.cer";

/**
 * @param args null
 * @throws Exception /
 */
public static void main(String[] args) throws Exception {

     // -- ГОСТ Р 34.10-2001 --

    //получение сертификата и запись его в хранилище
    writeCertSample(KEY_ALG_2001, JCP.GOST_EL_SIGN_NAME, ALIAS_2001,
        STORE_PATH_2001, DNAME_2001);
    //чтение сертификата из хранилища и запись его в файл
    readCertSample(STORE_PATH_2001, ALIAS_2001, CERT_PATH_2001);
    //построение цепочки сертификатов
    // (требуется наличие сертификатов в хранилище/носителе)
    //certificateChain();

    // -- ГОСТ Р 34.10-2012 (256) --

    //получение сертификата и запись его в хранилище
    writeCertSample(KEY_ALG_2012_256, JCP.GOST_SIGN_2012_256_NAME,
        ALIAS_2012_256, STORE_PATH_2012_256, DNAME_2012_256);
    //чтение сертификата из хранилища и запись его в файл
    readCertSample(STORE_PATH_2012_256, ALIAS_2012_256, CERT_PATH_2012_256);

    // -- ГОСТ Р 34.10-2012 (512) --

    //получение сертификата и запись его в хранилище
    writeCertSample(KEY_ALG_2012_512, JCP.GOST_SIGN_2012_512_NAME,
        ALIAS_2012_512, STORE_PATH_2012_512, DNAME_2012_512);
    //чтение сертификата из хранилища и запись его в файл
    readCertSample(STORE_PATH_2012_512, ALIAS_2012_512, CERT_PATH_2012_512);
}

/**
 * Пример генерирования запроса, отправки запроса центру сертификации и записи
 * полученного от центра сертификата в хранилище доверенных сертификатов
 *
 * @param keyAlg Алгоритм ключа.
 * @param signAlg Алгоритм подписи.
 * @param alias Алиас ключа для сохранения.
 * @param storePath Путь к хранилищу сертификатов.
 * @param dnName DN-имя сертификата.
 * @throws Exception /
 */
public static void writeCertSample(String keyAlg, String signAlg,
    String alias, String storePath, String dnName) throws Exception {
    /* Генерирование ключевой пары в соответствии с которой будет создан запрос
    на сертификат*/
    KeyPair keypair = KeyPairGen.genKey(keyAlg);
    // отправка запроса центру сертификации и получение от центра
    // сертификата в DER-кодировке
    byte[] encoded = createRequestAndGetCert(keypair, signAlg, JCP.PROVIDER_NAME, dnName);

    // инициализация генератора X509-сертификатов
    CertificateFactory cf = CertificateFactory.getInstance("X509");
    // генерирование X509-сертификата из закодированного представления сертификата
    Certificate cert =
            cf.generateCertificate(new ByteArrayInputStream(encoded));

    /* Запись полученного от центра сертификата*/
    // инициализация хранилища доверенных сертификатов именем ключевого носителя
    // (жесткий диск)
    KeyStore keyStore = KeyStore.getInstance(STORE_TYPE);
    // загрузка содержимого хранилища (предполагается, что инициализация
    // хранилища именем CertStoreName производится впервые, т.е. хранилища
    // с таким именем пока не существует)
    keyStore.load(null, null);

    // запись сертификата в хранилище доверенных сертификатов
    // (предполагается, что на носителе с именем CertStoreName не существует
    // ключа с тем же именем alias)
    keyStore.setCertificateEntry(alias, cert);

    // определение пути к файлу для сохранения в него содержимого хранилища
    File file = new File(storePath);
    // сохранение содержимого хранилища в файл
    keyStore.store(new FileOutputStream(file), STORE_PASS);
}

/**
 * Пример чтения сертификата из хранилища и записи его в файл
 *
 * @param storePath Путь к хранилищу сертификатов.
 * @param alias Алиас ключа подписи.
 * @param certPath Путь к файлу сертификата.
 * @throws Exception /
 */
public static void readCertSample(String storePath, String alias,
    String certPath) throws Exception {
    /* Чтение сертификата их хранилища доверенных сертификатов */
    // инициализация хранилища доверенных сертификатов именем ключевого носителя
    // (жесткий диск)
    final KeyStore keyStore = KeyStore.getInstance(STORE_TYPE);
    // определение пути к файлу для чтения содержимого хранилища
    // и последующего его сохранения
    final File file = new File(storePath);
    // загрузка содержимого хранилища (предполагается, что хранилище,
    // проинициализированное именем CertStoreName существует)
    keyStore.load(new FileInputStream(file), STORE_PASS);

    // чтение сертификата из хранилища доверенных сертификатов
    // (предполагается, что на носителе с именем CertStoreName не существует
    // ключа с тем же именем alias)
    final Certificate cert = keyStore.getCertificate(alias);

    // сохранение содержимого хранилища в файл с тем же паролем
    keyStore.store(new FileOutputStream(file), STORE_PASS);

    /* Запись прочитанного сертификата в файл */
    // определение пути к файлу для записи в него сертификата
    final File cert_file = new File(certPath);
    // кодирование сертификата в DER-кодировку
    final byte[] encoded = cert.getEncoded();
    // запись закодированного сертификата в файл
    final FileOutputStream outStream = new FileOutputStream(cert_file);
    outStream.write(encoded);
}

/**
 * Чтение корневого, промежуточного сертификатов из хранилища доверенных
 * сертификатов, сертификата открытого ключа - с носителя. Предполагается что
 * все читаемые сертификаты ранее были записаны на носитель и в хранилище.
 *
 * @throws Exception /
 */
public static void certificateChain() throws Exception {

    // уникальное имя корневого сертификата
    final String aliasRootCert = "rootCert";
    // уникальное имя промежуточного сертификата
    final String aliasInterCert = "intermediateCert";
    // уникальное имя сертификата открытого ключа
    final String aliasEndCert = "endCert";

    // инициализация хранилища доверенных сертификатов и ключевого носителя
    final KeyStore keyStore = KeyStore.getInstance(STORE_TYPE);

    // загрузка содержимого хранилища (предполагается, что хранилище,
    // проинициализированное именем STORE_TYPE существует) и содержимого
    // ключевого носителя
    keyStore.load(new FileInputStream(STORE_PATH_2001), STORE_PASS);

    // чтение корневого сертификата из хранилища доверенных сертификатов
    // (предполагается, что такой сертификат существует в хранилище)
    final Certificate certRoot = keyStore.getCertificate(aliasRootCert);

    // чтение промежуточного сертификата из хранилища доверенных сертификатов
    // (предполагается, что такой сертификат существует в хранилище)
    final Certificate certInter = keyStore.getCertificate(aliasInterCert);

    // чтение конечного сертификата (сертификата открытого ключа) с носителя
    // (предполагается, что сертификат такой сертификат существует на носителе)
    final Certificate certEnd = keyStore.getCertificate(aliasEndCert);

    // сохранение содержимого хранилища в файл с тем же паролем
    keyStore.store(new FileOutputStream(STORE_PATH_2001), STORE_PASS);

    //Построение цепочки из прочитанных сертификатов, начиная с корневого сертификата
    //(с именем aliasRootCert) и заканчивая сертификатом открытого ключа (c именем aliasEndCert)

    // определение списка сертификатов, из которых
    // осуществляется построение цепочки
    final List certs = new ArrayList(3);
    certs.add(certRoot);
    certs.add(certInter);
    certs.add(certEnd);

    // определение корневого сертификата (с которого начинается построение
    // цепочки)
    final TrustAnchor anchor =
            new TrustAnchor((X509Certificate) certRoot, null);

    // определение параметров специального хранилища
    // сертификатов, в которое записываются все используемые
    // в построении цепочки сертификаты
    final CollectionCertStoreParameters par =
            new CollectionCertStoreParameters(certs);

    // создание специального хранилища сертификатов на основе
    // параметров, определенных списком сертификатов
    final CertStore store = CertStore.getInstance("Collection", par);

    // инициализация объекта построения цепочки сертификатов
    final CertPathBuilder cpb = CertPathBuilder.getInstance("PKIX");
    //или для совместимости с КриптоПро УЦ
    //CertPathBuilder cpb = CertPathBuilder.getInstance("CPPKIX");

    // инициализация параметров построения цепочки сертификатов
    final PKIXBuilderParameters params = new PKIXBuilderParameters(
            Collections.singleton(anchor), new X509CertSelector());

    // добавление к параметрам сертификатов, из которых
    // будет строиться цепочка
    params.addCertStore(store);

    // инициализация объекта выборки сертификата, которым
    // заканчивается построение цепочки
    final X509CertSelector selector = new X509CertSelector();

    // определение сертификата, которым
    // заканчивается построение цепочки
    selector.setCertificate((X509Certificate) certEnd);

    params.setTargetCertConstraints(selector);

    // построение цепочки сертификатов
    final PKIXCertPathBuilderResult res =
            (PKIXCertPathBuilderResult) cpb.build(params);

    /* Проверка построенной цепочки сертификатов */

    // инициализация объекта проверки цепочки сертификатов
    final CertPathValidator validator = CertPathValidator.getInstance("PKIX");
    //или для совместимости с КриптоПро УЦ
    //CertPathValidator validator = CertPathValidator.getInstance("CPPKIX");

    // проверка цепочки сертификатов
    final CertPathValidatorResult val_res =
            validator.validate(res.getCertPath(), params);

    // вывод результата проверки в строком виде
    System.out.println(val_res.toString());
}

/**
 * Функция формирует запрос на сертификат, отправляет запрос центру сертификации
 * и получает от центра сертификат.
 *
 * @param pair ключевая пара. Открытый ключ попадает в запрос на сертификат,
 * секретный ключ для подписи запроса.
 * @param signAlgorithm Алгоритм подписи.
 * @param signatureProvider Провайдер подписи.
 * @param dnName DN-имя сертификата.
 * @return сертификат в DER-кодировке
 * @throws Exception errors
 */
public static byte[] createRequestAndGetCert(KeyPair pair, String signAlgorithm,
    String signatureProvider, String dnName) throws Exception {

    // формирование запроса
    GostCertificateRequest request = createRequest(pair,
        signAlgorithm, signatureProvider, dnName);

    // отправка запроса центру сертификации и получение от центра
    // сертификата в DER-кодировке
    return request.getEncodedCert(HTTP_ADDRESS);
}

/**
 * Функция формирует запрос на сертификат.
 *
 * @param pair ключевая пара. Открытый ключ попадает в запрос на сертификат,
 * секретный ключ для подписи запроса.
 * @param signAlgorithm Алгоритм подписи.
 * @param signatureProvider Провайдер подписи.
 * @param dnName DN-имя сертификата.
 * @return запрос
 * @throws Exception errors
 */
public static GostCertificateRequest createRequest(KeyPair pair, String signAlgorithm,
    String signatureProvider, String dnName) throws Exception {
    /* Генерирование запроса на сертификат в соответствии с открытым ключом*/
    // создание генератора запроса на сертификат
    GostCertificateRequest request = new GostCertificateRequest(signatureProvider);
    // инициализация генератора
    // @deprecated с версии 1.0.48
    // вместо init() лучше использовать setKeyUsage() и addExtKeyUsage()
    // request.init(KEY_ALG);

    /*
    Установить keyUsage способ использования ключа можно функцией
    setKeyUsage. По умолчанию для ключа подписи, т.е. для указанного в первом
    параметре функции init() алгоритма "GOST3410EL" используется комбинация
    DIGITAL_SIGNATURE | NON_REPUDIATION. Для ключа шифрования, т.е. для
    алгоритма "GOST3410DHEL" добавляется KEY_ENCIPHERMENT | KEY_AGREEMENT.
    */
    final String keyAlgorithm = pair.getPrivate().getAlgorithm();
    if (keyAlgorithm.equalsIgnoreCase(JCP.GOST_EL_DEGREE_NAME) ||
        keyAlgorithm.equalsIgnoreCase(JCP.GOST_EL_2012_256_NAME) ||
        keyAlgorithm.equalsIgnoreCase(JCP.GOST_EL_2012_512_NAME)) {
        int keyUsage = GostCertificateRequest.DIGITAL_SIGNATURE |
            GostCertificateRequest.NON_REPUDIATION;
        request.setKeyUsage(keyUsage);
    } // if
    else {
        int keyUsage = GostCertificateRequest.DIGITAL_SIGNATURE |
            GostCertificateRequest.NON_REPUDIATION |
            GostCertificateRequest.KEY_ENCIPHERMENT |
            GostCertificateRequest.KEY_AGREEMENT;
        request.setKeyUsage(keyUsage);
    } // else

    /*
    Добавить ExtendedKeyUsage можно так. По умолчанию для ключа подписи,
    т.е. для алгоритма "GOST3410EL" список будет пустым. Для ключа
    шифрования, т.е. для алгоритма "GOST3410DHEL" добавляется OID
    INTS_PKIX_CLIENT_AUTH "1.3.6.1.5.5.7.3.2", а при установленном в true
    втором параметре функции init() еще добавляется INTS_PKIX_SERVER_AUTH
    "1.3.6.1.5.5.7.3.1"
    */
    request.addExtKeyUsage(GostCertificateRequest.INTS_PKIX_EMAIL_PROTECTION);
    /**
     * ExtendedKeyUsage можно указывать строкой "1.3.6.1.5.5.7.3.3", или можно
     * массивом int[]{1, 3, 6, 1, 5, 5, 7, 3, 4} или объектом типа
     * ru.CryptoPro.JCP.params.OID
     */
    request.addExtKeyUsage("1.3.6.1.5.5.7.3.3");
    /**
     * пример добавления в запрос собственного расширения Basic Constraints
     */

    Extension ext = new Extension();
    int[] extOid = {2, 5, 29, 19};
    ext.extnID = new Asn1ObjectIdentifier(extOid);
    ext.critical = new Asn1Boolean(true);
    byte[] extValue = {48, 6, 1, 1, -1, 2, 1, 5};
    ext.extnValue = new Asn1OctetString(extValue);
    request.addExtension(ext);

    /*
    //1

    Extension basic;
    byte[] enc;
    Asn1BerEncodeBuffer buf = new Asn1BerEncodeBuffer();

    basic = new Extension();
    basic.extnID = new Asn1ObjectIdentifier(ALL_CertificateExtensionsValues.id_ce_basicConstraints);

    basic.critical = new Asn1Boolean(false);
    BasicConstraintsSyntax basicVal = new BasicConstraintsSyntax();

    basicVal.encode(buf);
    enc = buf.getMsgCopy();

    basic.extnValue = new Asn1OctetString(enc);
    request.addExtension(basic);

    //2

    Extension unknown;
    buf = new Asn1BerEncodeBuffer();

    unknown = new Extension();
    unknown.extnID = new Asn1ObjectIdentifier(new int[] {1,2,643,3,123,3,1});

    unknown.critical = new Asn1Boolean(false);
    Asn1UTF8String unknownValue = new Asn1UTF8String("V2QL0020sИванов");

    unknownValue.encode(buf);
    enc = buf.getMsgCopy();

    unknown.extnValue = new Asn1OctetString(enc);
    request.addExtension(unknown);

    //3

    Extension oidExt;
    buf = new Asn1BerEncodeBuffer();

    oidExt = new Extension();
    oidExt.extnID = new Asn1ObjectIdentifier(new int[] {1,2,643,3,123,3,4});

    oidExt.critical = new Asn1Boolean(false);
    Asn1ObjectIdentifier oid = new Asn1ObjectIdentifier(new int[] {1,2,643,3,123,5,4});

    oid.encode(buf);
    enc = buf.getMsgCopy();

    oidExt.extnValue = new Asn1OctetString(enc);
    request.addExtension(oidExt);

    //4

    Extension extAlt = new Extension();
    int[] extOidAlt = {2, 5, 29, 17};
    extAlt.extnID = new Asn1ObjectIdentifier(extOidAlt);
    extAlt.critical = new Asn1Boolean(false);

    InetAddress address = InetAddress.getByName("172.24.8.31");
    byte [] address_ip = address.getAddress();

    GeneralName name = new GeneralName();
    name.set_iPAddress(new Asn1OctetString(address_ip)); // ip v4 - 4 байта

    GeneralNames names = new GeneralNames(new GeneralName[] {name});
    buf = new Asn1BerEncodeBuffer();

    names.encode(buf);
    enc = buf.getMsgCopy();

    extAlt.extnValue = new Asn1OctetString(enc);
    request.addExtension(extAlt);
    */

    // определение параметров и значения открытого ключа
    request.setPublicKeyInfo(pair.getPublic());
    // определение имени субъекта для создания запроса
    request.setSubjectInfo(dnName);
    // подпись сертификата на закрытом ключе и кодирование запроса
    request.encodeAndSign(pair.getPrivate(), signAlgorithm);

    return request;
}

}
