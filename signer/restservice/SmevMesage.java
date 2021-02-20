package restservice;

public class SmevMesage {

	private String id;
	private String xml;

	public SmevMesage(String id, String xml) {
		super();
		this.id = id;
		this.xml = xml;
	}

	public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getXml() {
        return xml;
    }

    public void setXml(String xml) {
        this.xml = xml;
    }

    @Override
    public String toString() {
        return new StringBuffer().append(getXml()).toString();
    }
}