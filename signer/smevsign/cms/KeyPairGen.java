/**
 * $RCSfile$
 * version $Revision$
 * created 14.04.2005 17:40:17 by elvira
 * last modified $Date$ by $Author$
 * (C) ООО Крипто-Про 2004-2009.
 *
 * modifyed by gosha20777 <gosha20777@live.ru>
 * (C) 2020
 */
package smevsign.cms;

import ru.CryptoPro.JCP.JCP;
import ru.CryptoPro.JCP.params.AlgIdSpec;
import ru.CryptoPro.JCP.params.CryptDhAllowedSpec;
import ru.CryptoPro.JCP.params.OID;
import ru.CryptoPro.JCPRequest.GostCertificateRequest;

import java.io.ByteArrayInputStream;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.cert.Certificate;
import java.security.cert.CertificateFactory;

/**
 * В данном примере осуществляется генерирование ключевой пары в соответствии с
 * алгоритмом ГОСТ Р 34.10-2001, генерирование сертификата созданного открытого
 * ключа, последующее сохранение в ключевом контейнере созданного закрытого
 * ключа и соответвующего ему сертификата открытого ключа, а также чтение только
 * что записанного ключа из контейнера.
 */
public class KeyPairGen {

// -- ГОСТ Р 34.10-2001 -- //

/**
 * имя контейнера A
 */
public static final String CONT_NAME_A_2001 = "Cont_A";
/**
 * пароль на контейнер A
 */
public static final char[] PASSWORD_A_2001 = "a".toCharArray();
/**
 * имя субъекта сертификата A
 */
public static final String DNAME_A_2001 = "CN=Container_A, O=CryptoPro, C=RU";
/**
 * имя контейнера B
 */
public static final String CONT_NAME_B_2001 = "Cont_B";
/**
 * пароль на контейнер B
 */
public static final char[] PASSWORD_B_2001 = "b".toCharArray();
/**
 * имя субъекта сертификата B
 */
public static final String DNAME_B_2001 = "CN=Container_B, O=CryptoPro, C=RU";

// -- ГОСТ Р 34.10-2012 (256) -- //

/**
 * имя контейнера A
 */
public static final String CONT_NAME_A_2012_256 = "Cont_A_2012_256";
/**
 * пароль на контейнер A
 */
public static final char[] PASSWORD_A_2012_256 = "a2".toCharArray();
/**
 * имя субъекта сертификата A
 */
public static final String DNAME_A_2012_256 = "CN=Container_A_2012_256, O=CryptoPro, C=RU";
/**
 * имя контейнера B
 */
public static final String CONT_NAME_B_2012_256 = "Cont_B_2012_256";
/**
 * пароль на контейнер B
 */
public static final char[] PASSWORD_B_2012_256 = "b2".toCharArray();
/**
 * имя субъекта сертификата B
 */
public static final String DNAME_B_2012_256 = "CN=Container_B_2012_256, O=CryptoPro, C=RU";

// -- ГОСТ Р 34.10-2012 (512) -- //

/**
 * имя контейнера A
 */
public static final String CONT_NAME_A_2012_512 = "Cont_A_2012_512";
/**
 * пароль на контейнер A
 */
public static final char[] PASSWORD_A_2012_512 = "a3".toCharArray();
/**
 * имя субъекта сертификата A
 */
public static final String DNAME_A_2012_512 = "CN=Container_A_2012_512, O=CryptoPro, C=RU";
/**
 * имя контейнера B
 */
public static final String CONT_NAME_B_2012_512 = "Cont_B_2012_512";
/**
 * пароль на контейнер B
 */
public static final char[] PASSWORD_B_2012_512 = "b3".toCharArray();
/**
 * имя субъекта сертификата B
 */
public static final String DNAME_B_2012_512 = "CN=Container_B_2012_512, O=CryptoPro, C=RU";

/**
 * @param args null
 * @throws Exception
 */
public static void main(String[] args) throws Exception {

    main_(Constants.SIGN_KEY_PAIR_ALG_2001,
        CONT_NAME_A_2001, PASSWORD_A_2001, DNAME_A_2001,
        CONT_NAME_B_2001, PASSWORD_B_2001, DNAME_B_2001);

    main_(Constants.SIGN_KEY_PAIR_ALG_2012_256,
        CONT_NAME_A_2012_256, PASSWORD_A_2012_256, DNAME_A_2012_256,
        CONT_NAME_B_2012_256, PASSWORD_B_2012_256, DNAME_B_2012_256);

    main_(Constants.SIGN_KEY_PAIR_ALG_2012_512,
        CONT_NAME_A_2012_512, PASSWORD_A_2012_512, DNAME_A_2012_512,
        CONT_NAME_B_2012_512, PASSWORD_B_2012_512, DNAME_B_2012_512);
}

/**
 * Генерация пары.
 *
 * @param keyAlg Алгоритм ключа.
 * @param contNameA Алиас ключа А.
 * @param passA Пароль к ключу А.
 * @param dNameA Имя сертификата А.
 * @param contNameB Алиас ключа В.
 * @param passB Пароль к ключу В.
 * @param dNameB Имя сертификата В.
 * @throws Exception
 */
public static void main_(String keyAlg, String contNameA, char[] passA, String dNameA,
    String contNameB, char[] passB, String dNameB) throws Exception {

    //генерирование ключевой пары ЭЦП и запись в хранилище
    saveKeyWithCert(genKey(keyAlg), contNameA, passA, dNameA);

    // default ГОСТ Р 34.10-2001
    OID keyOid = new OID("1.2.643.2.2.19");
    OID signOid = new OID("1.2.643.2.2.35.2");
    OID digestOid = new OID("1.2.643.2.2.30.1");
    OID cryptOid = new OID("1.2.643.2.2.31.1");

    if (keyAlg.equals(JCP.GOST_EL_2012_256_NAME)) {
        keyOid = new OID("1.2.643.7.1.1.1.1");
        signOid = new OID("1.2.643.2.2.35.2");
        digestOid = new OID("1.2.643.7.1.1.2.2");
        cryptOid = new OID("1.2.643.7.1.2.5.1.1");
    } else if (keyAlg.equals(JCP.GOST_EL_2012_512_NAME)) {
        keyOid = new OID("1.2.643.7.1.1.1.2");
        signOid = new OID("1.2.643.7.1.2.1.2.1");
        digestOid = new OID("1.2.643.7.1.1.2.3");
        cryptOid = new OID("1.2.643.7.1.2.5.1.1");
    }

    //генерирование ключевой пары ЭЦП с параметрами и запись в хранилище
    saveKeyWithCert(genKeyWithParams(keyAlg, keyOid, signOid,
        digestOid, cryptOid), contNameB, passB, dNameB);

    // загрузка содержимого хранилища для чтения ключа
    final KeyStore hdImageStore = KeyStore.getInstance(Constants.KEYSTORE_TYPE);
    // загрузка содержимого носителя (предполагается, что не существует
    // хранилища доверенных сертификатов)
    hdImageStore.load(null, null);

    // получение закрытого ключа из хранилища
    final PrivateKey keyA = (PrivateKey) hdImageStore.getKey(contNameA, passA);
    final PrivateKey keyB = (PrivateKey) hdImageStore.getKey(contNameB, passB);

    System.out.println("OK");
}

/**
 * генерирование ключевой пары
 *
 * @param algorithm алгоритм
 * @return ключевая пара
 * @throws Exception /
 */
public static KeyPair genKey(String algorithm)
        throws Exception {

    // создание генератора ключевой пары
    final KeyPairGenerator keyGen = KeyPairGenerator.getInstance(algorithm);

    // генерирование ключевой пары
    return keyGen.generateKeyPair();
}

/**
 * генерирование ключевой пары
 *
 * @param algorithm алгоритм
 * @return ключевая пара
 * @throws Exception /
 */
public static KeyPair genKeyAllowDh(String algorithm)
        throws Exception {

    // создание генератора ключевой пары
    final KeyPairGenerator keyGen = KeyPairGenerator.getInstance(algorithm);

    // разрешаем согласование на ключах подписи, если это ключ подписи
    keyGen.initialize(new CryptDhAllowedSpec());

    // генерирование ключевой пары
    return keyGen.generateKeyPair();
}

/**
 * генерирование ключевой пары с параметрами
 *
 * @param algorithm алгоритм
 * @return ключевая пара
 * @throws Exception /
 */
public static KeyPair genKeyWithParams(String algorithm, OID keyOid,
    OID signOid, OID digestOid, OID cryptOid) throws Exception {

    // создание генератора ключевой пары ЭЦП
    final KeyPairGenerator keyGen = KeyPairGenerator.getInstance(algorithm);

    // определение параметров генератора ключевой пары
    final AlgIdSpec keyParams =
            new AlgIdSpec(keyOid, signOid, digestOid, cryptOid);
    keyGen.initialize(keyParams);

    // генерирование ключевой пары
    return keyGen.generateKeyPair();
}

/**
 * Сохранение в хранилище
 *
 * @param pair сгенерированная ключевая пара
 * @param contName имя контейнера
 * @param password пароль на контенер
 * @param dname имя субъекта сертификата
 * @throws Exception /
 */
public static void saveKeyWithCert(KeyPair pair, String contName,
    char[] password, String dname) throws Exception {

    //* создание цепочки сертификатов, состоящей из самоподписанного сертификата
    final Certificate[] certs = new Certificate[1];
    certs[0] = genSelfCert(pair, dname);

    //* запись закрытого ключа и цепочки сертификатов в хранилище
    // определение типа ключевого носителя, на который будет осуществлена запись ключа
    final KeyStore hdImageStore = KeyStore.getInstance(Constants.KEYSTORE_TYPE);
    // загрузка содержимого носителя (предполагается, что не существует
    // хранилища доверенных сертификатов)
    hdImageStore.load(null, null);
    // запись на носитель закрытого ключа и цепочки
    hdImageStore.setKeyEntry(contName, pair.getPrivate(), password, certs);
    // сохранение содержимого хранилища
    hdImageStore.store(null, null);
}

/**
 * Генерирование самоподписанного сертификата
 *
 * @param pair ключевая пара
 * @param dname имя субъекта сертификата
 * @return самоподписанный сертификат
 * @throws Exception /
 */
public static Certificate genSelfCert(KeyPair pair, String dname)
        throws Exception {
    // создание генератора самоподписанного сертификата
    final GostCertificateRequest gr = new GostCertificateRequest();
    // генерирование самоподписанного сертификата, возвращаемого в DER-кодировке
    final byte[] enc = gr.getEncodedSelfCert(pair, dname);
    // инициализация генератора X509-сертификатов
    final CertificateFactory cf =
            CertificateFactory.getInstance(Constants.CF_ALG);
    // генерирование X509-сертификата из закодированного представления сертификата
    return cf.generateCertificate(new ByteArrayInputStream(enc));
}
}
