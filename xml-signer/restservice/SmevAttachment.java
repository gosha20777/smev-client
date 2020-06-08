package restservice;

public class SmevAttachment {

    private String fileName;
    private String mimeType;
    private String signature;
    private String content;

    public SmevAttachment(String fileName, String mimeType, String signature, String content) {
        super();
        this.fileName = fileName;
        this.mimeType = mimeType;
        this.signature = signature;
        this.content = content;
    }

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
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

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }
}