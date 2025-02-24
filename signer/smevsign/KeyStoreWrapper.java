package smevsign;

import static smevsign.Resources.JCP_STORE_NAME;

import java.io.ByteArrayInputStream;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.security.cert.Certificate;

public class KeyStoreWrapper {
	private static KeyStore keyStore;
	private static boolean isInit;

	private static void init() throws Exception {
		keyStore = KeyStore.getInstance(JCP_STORE_NAME);
		keyStore.load(null);
		isInit = true;
	}

	public static PrivateKey getPrivateKey(String alias, char[] password) throws Exception {
		if (!isInit) init();
		return (PrivateKey) keyStore.getKey(alias, password);
	}

	public static X509Certificate getX509Certificate(String alias) throws Exception {
		if (!isInit) init();
		if (!keyStore.containsAlias(alias))
			throw new Exception("No such alias in keystore: " + alias);
		X509Certificate certificate = (X509Certificate) keyStore.getCertificate(alias);
		if (certificate == null)
			throw new Exception("No certificate in alias: " + alias);
		return (X509Certificate) CertificateFactory.getInstance("X509").generateCertificate(new ByteArrayInputStream(certificate.getEncoded()));
	}

	public static Certificate getCertificate(String alias) throws Exception {
		if (!isInit) init();
		if (!keyStore.containsAlias(alias))
			throw new Exception("No such alias in keystore: " + alias);
		Certificate certificate = keyStore.getCertificate(alias);
		if (certificate == null)
			throw new Exception("No certificate in alias: " + alias);
		return CertificateFactory.getInstance("X509").generateCertificate(new ByteArrayInputStream(certificate.getEncoded()));
	}
}