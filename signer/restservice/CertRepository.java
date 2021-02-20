package restservice;

import java.util.HashMap;
import java.util.Map;

public class CertRepository {
    private Map<String, CertDescription> certs = new HashMap<String, CertDescription>();

	public CertRepository(Map<String, CertDescription> certs) {
        super();
        this.certs = certs;
	}

	public Map<String, CertDescription> getCerts() {
        return certs;
    }

    public void setCerts(Map<String, CertDescription> certs) {
        this.certs = certs;
    }
}