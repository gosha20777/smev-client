package restservice;

public class SmevAttachment {

    private String hash;
    private String mimeType;
    private String signature;

    public SmevAttachment(String hash, String mimeType, String signature) {
        super();
        this.hash = hash;
        this.mimeType = mimeType;
        this.signature = signature;
    }

    public String getHash() {
        return hash;
    }

    public void setHash(String hash) {
        this.hash = hash;
    }

    public String getMimeType() {
        return mimeType;
    }

    public void setMimeType(String mimeType) {
        this.mimeType = mimeType;
    }

    public String getSignature() {
        return signature;
    }

    public void setSignature(String signature) {
        this.signature = signature;
    }
}