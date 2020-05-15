package restservice;

public class CertDescription {

	private String alias;
	private String password;

	public CertDescription(String alias, String password) {
		super();
		this.alias = alias;
		this.password = password;
	}

	public String getAlias() {
        return alias;
    }

    public void setAlias(String alias) {
        this.alias = alias;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    @Override
    public String toString() {
        return new StringBuffer().append(getAlias()).toString();
    }
}