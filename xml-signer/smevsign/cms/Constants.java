/**
 * $RCSfile$
 * version $Revision$
 * created 26.05.2009 15:07:10 by kunina
 * last modified $Date$ by $Author$
 * (C) ООО Крипто-Про 2004-2009.
 *
 * modifyed by gosha20777 <gosha20777@live.ru>
 * (C) 2020
 */
package smevsign.cms;

import ru.CryptoPro.JCP.JCP;

/**
 * Константы для примеров.
 *
 * @author Copyright 2004-2009 Crypto-Pro. All rights reserved.
 * @.Version
 */
public class Constants {

/** Алгоритмы **/

/**
 * алгоритм ключа подписи: "GOST3410EL" или JCP.GOST_EL_DEGREE_NAME
 */
public static final String SIGN_KEY_PAIR_ALG_2001 = JCP.GOST_EL_DEGREE_NAME;
/**
 * алгоритм ключа подписи: "GOST3410_2012_256" или JCP.GOST_EL_2012_256_NAME
 */
public static final String SIGN_KEY_PAIR_ALG_2012_256 = JCP.GOST_EL_2012_256_NAME;
/**
 * алгоритм ключа подписи: "GOST3410_2012_512" или JCP.GOST_EL_2012_512_NAME
 */
public static final String SIGN_KEY_PAIR_ALG_2012_512 = JCP.GOST_EL_2012_512_NAME;
/**
 * алгоритм ключа обмена: "GOST3410DHEL" или JCP.GOST_EL_DH_NAME
 */
public static final String EXCH_KEY_PAIR_ALG_2001 = JCP.GOST_EL_DH_NAME;
/**
 * алгоритм ключа обмена: "GOST3410DH_2012_256" или JCP.GOST_DH_2012_256_NAME
 */
public static final String EXCH_KEY_PAIR_ALG_2012_256 = JCP.GOST_DH_2012_256_NAME;
/**
 * алгоритм ключа обмена: "GOST3410DH_2012_512" или JCP.GOST_DH_2012_512_NAME
 */
public static final String EXCH_KEY_PAIR_ALG_2012_512 = JCP.GOST_DH_2012_512_NAME;
/**
 * стандарт сертификата "X509" или JCP.CERTIFICATE_FACTORY_NAME
 */
public static final String CF_ALG = "X509";
/**
 * алгоритм шифрования ГОСТ 28147-89: "GOST28147" или CryptoProvider.GOST_CIPHER_NAME
 */
public static final String CHIPHER_ALG = "GOST28147";
/**
 * алгоритм хеширования ГОСТ Р 34.11-94: "GOST3411" или JCP.GOST_DIGEST_NAME
 */
public static final String DIGEST_ALG_2001 = JCP.GOST_DIGEST_NAME;
/**
 * алгоритм хеширования ГОСТ Р 34.11-2012 (256): "GOST3411_2012_256" или
 * JCP.GOST_DIGEST_2012_256_NAME
 */
public static final String DIGEST_ALG_2012_256 = JCP.GOST_DIGEST_2012_256_NAME;
/**
 * алгоритм хеширования ГОСТ Р 34.11-2012 (512): "GOST3411_2012_512" или
 * JCP.GOST_DIGEST_2012_512_NAME
 */
public static final String DIGEST_ALG_2012_512 = JCP.GOST_DIGEST_2012_512_NAME;
/**
 * алгоритм подписи ГОСТ Р 34.10-2001: "GOST3411withGOST3410EL" или
 * JCP.GOST_EL_SIGN_NAME
 */
public static final String SIGN_EL_ALG_2001 = JCP.GOST_EL_SIGN_NAME;
/**
 * алгоритм подписи ГОСТ Р 34.10-2012 (256): "GOST3411_2012_256withGOST3410_2012_256" или
 * JCP.GOST_SIGN_2012_256_NAME
 */
public static final String SIGN_EL_ALG_2012_256 = JCP.GOST_SIGN_2012_256_NAME;
/**
 * алгоритм подписи ГОСТ Р 34.10-2012 (512): "GOST3411_2012_512withGOST3410_2012_512" или
 * JCP.GOST_SIGN_2012_512_NAME
 */
public static final String SIGN_EL_ALG_2012_512 = JCP.GOST_SIGN_2012_512_NAME;
/**
 * алгоритм подписи ГОСТ Р 34.10-2001 (используется для совеместимости с
 * криптопровайдером CryptoPro CSP): "CryptoProSignature" или
 * JCP.CRYPTOPRO_SIGN_NAME
 */
public static final String SIGN_CP_ALG_2001 = JCP.CRYPTOPRO_SIGN_NAME;
/**
 * алгоритм подписи ГОСТ Р 34.10-2012 (256) (используется для совеместимости с
 * криптопровайдером CryptoPro CSP): "CryptoProSignature_2012_256" или
 * JCP.CRYPTOPRO_SIGN_2012_256_NAME
 */
public static final String SIGN_CP_ALG_2012_256 = JCP.CRYPTOPRO_SIGN_2012_256_NAME;
/**
 * алгоритм подписи ГОСТ Р 34.10-2012 (512) (используется для совеместимости с
 * криптопровайдером CryptoPro CSP): "CryptoProSignature_2012_512" или
 * JCP.CRYPTOPRO_SIGN_2012_512_NAME
 */
public static final String SIGN_CP_ALG_2012_512 = JCP.CRYPTOPRO_SIGN_2012_512_NAME;

/**
 * датчик случайных чисел: "CPRandom" или JCP.CP_RANDOM
 */
public static final String RANDOM_ALG = "CPRandom";

/** Параметры для работы с ключами и сертификатами **/
/**
 * тип хранилища:
 * <p/>
 * "HDImageStore" - жесткий диск
 * <p/>
 * "FloppyStore" - дискета, флешка
 * <p/>
 * "OCFStore" или "J6CFStore" - карточка
 */
public static final String KEYSTORE_TYPE = JCP.HD_STORE_NAME;

/** Вспомогательные функции и параметры **/
/**
 * hex-string
 *
 * @param array массив данных
 * @return hex-string
 */
public static String toHexString(byte[] array) {
    final char[] hex = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A',
            'B', 'C', 'D', 'E', 'F'};
    StringBuffer ss = new StringBuffer(array.length * 3);
    for (int i = 0; i < array.length; i++) {
        ss.append(' ');
        ss.append(hex[(array[i] >>> 4) & 0xf]);
        ss.append(hex[array[i] & 0xf]);
    }
    return ss.toString();
}
}
