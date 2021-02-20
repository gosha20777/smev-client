package restservice;

public class SmevTeamplate {

    private String id;
    private String to;
    private String msgType;
    private String tagForSign;
    private String xml;
    private SmevAttachment attachment;

    public SmevTeamplate(String id, String to, String msgType, String xml, String tagForSign, SmevAttachment attachment) {
        super();
        this.id = id;
        this.to = to;
        this.msgType = msgType;
        this.tagForSign = tagForSign;
        this.xml = xml;
        this.attachment = attachment;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTo() {
        return to;
    }

    public void setTo(String to) {
        this.to = to;
    }

    public String getMsgType() {
        return msgType;
    }

    public void setMsgType(String msgType) {
        this.msgType = msgType;
    }

    public String getTagForSign() {
        return tagForSign;
    }

    public void setTagForSign(String tagForSign) {
        this.tagForSign = tagForSign;
    }

    public String getXml() {
        return xml;
    }

    public void setXml(String xml) {
        this.xml = xml;
    }

    public SmevAttachment getAttachment() {
        return attachment;
    }

    public void setAttachment(SmevAttachment attachment) {
        this.attachment = attachment;
    }

    @Override
    public String toString() {
        return new StringBuffer().append(getXml()).toString();
    }
}