//
// UTF-8
//
// -------------------------------------------------------------------
// SmevSigner (СМЭВ-3)
// -------------------------------------------------------------------
//
// Пакет классов smevsign для трансформации и подписания XML по методическим рекомендациям СМЭВ 3 взят отсюда:
//   https://github.com/Twayn/DigitalSignature
//     + внесены некоторые корректировки под текущую версию JRE
// @author gosha20777
//
package restservice;

import java.util.*;
import java.io.*;
import java.io.File;
import java.io.FileInputStream;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.security.PrivateKey;
import java.security.cert.X509Certificate;
import java.security.cert.Certificate;
import javax.xml.soap.SOAPMessage;
import com.fasterxml.uuid.Generators;
import static java.nio.charset.StandardCharsets.UTF_8;
import static smevsign.KeyStoreWrapper.getPrivateKey;
import static smevsign.KeyStoreWrapper.getX509Certificate;
import static smevsign.KeyStoreWrapper.getCertificate;
import smevsign.SignAttributesSupplier;
import smevsign.Signer;
import smevsign.cms.CMSSign;
import smevsign.*;

public class SmevTeamplateTransformer
{
    String KEY_ALIAS;
    String KEY_PASS;
    String APP_PATH;

    public SmevTeamplateTransformer(String keyAlias, String keyPassword) throws Exception {
        this.APP_PATH = SmevTeamplateTransformer.class.getProtectionDomain().getCodeSource().getLocation().getFile();
        this.KEY_ALIAS = keyAlias;
        this.KEY_PASS = keyPassword;
    }
    
    public SmevMesage Transform(SmevTeamplate teamplate, String shemeType) throws Exception {
        String XML_WRAPPER = "";
        String XML_OUTPUT = "";

        // метод / тип сообщения к СМЭВ : SendRequestRequest, GetResponseRequest, AckRequest
        String MSG_TYPE = teamplate.getMsgType();
        // ID элемента в XML на который следует поставить подпись
        String TAG_FOR_SIGN = teamplate.getTagForSign();
        // UUID сообщения
        String MESSAGE_ID = teamplate.getId();

        // проверяем входящий файл и читаем его в строку
        String XML_INPUT = teamplate.getXml();

        // проверяем файл с нужной оберткой запроса и читаем его в строку
        File wrapper_file = new File(this.APP_PATH+"wrap-"+MSG_TYPE+"-"+shemeType+".inc");
        if (!wrapper_file.isFile()) {
            throw new Exception("Wrapper file is not found for this MSG_TYPE. Check path to file or MSG_TYPE:\n "+APP_PATH+"wrap-"+MSG_TYPE+"-"+shemeType+".inc");
        }

        try {
            FileInputStream fis = new FileInputStream(wrapper_file);
            byte[] data = new byte[(int) wrapper_file.length()];
            fis.read(data);
            fis.close();
            XML_WRAPPER = new String(data,"UTF-8");
        } catch (Exception e) {
            throw new Exception("Can't read wrapper file content: "+APP_PATH+"wrap-"+MSG_TYPE+"-"+shemeType+".inc", e);
        }

        // оборачиваем входящее сообщение в обертку
        // и далее оперируем XML_INPUT
        XML_INPUT = XML_WRAPPER.replace("#REQUEST_BODY#",XML_INPUT);

        // берем входящий MessageID или генерируем новый
        if ( MESSAGE_ID.equals("0") ) {
            UUID uuid = Generators.timeBasedGenerator().generate();
            MESSAGE_ID = uuid.toString();
        }
        // вставляем MessageID в шаблон
        XML_INPUT = XML_INPUT.replace("#MESSAGE_ID#",MESSAGE_ID);

        // вставляем To в шаблон если это надо
        if (MSG_TYPE.equals("SendResponseRequest")){
            XML_INPUT = XML_INPUT.replace("#TO#",teamplate.getTo());
	        System.out.println("replace");
        }
        
        // вставляем вложение, если есть
        String ATTACHMENT_HEADER_LIST_WRAPPER = "";
        String ATTACHMENT_CONTENT_LIST_WRAPPER = "";
        if(teamplate.getAttachment() != null){
            //AttachmentHeaderList
            File attachment_header_list_file = new File(this.APP_PATH+"wrap-AttachmentHeaderList.inc");
            if (!attachment_header_list_file.isFile()) {
                throw new Exception("Wrapper file is not found. Check path to file:\n "+APP_PATH+"wrap-AttachmentHeaderList.inc");
            }

            try {
                FileInputStream fis = new FileInputStream(attachment_header_list_file);
                byte[] data = new byte[(int) attachment_header_list_file.length()];
                fis.read(data);
                fis.close();
                ATTACHMENT_HEADER_LIST_WRAPPER = new String(data,"UTF-8");
            } catch (Exception e) {
                throw new Exception("Can't read wrapper file content: wrap-AttachmentHeaderList.inc", e);
            }

            //AttachmentHeader
            String ATTACHMENT_HEADER_WRAPPER = "";
            File attachment_header_file = new File(this.APP_PATH+"wrap-AttachmentHeader.inc");
            if (!attachment_header_file.isFile()) {
                throw new Exception("Wrapper file is not found. Check path to file:\n "+APP_PATH+"wrap-AttachmentHeader.inc");
            }
            
            try {
                FileInputStream fis = new FileInputStream(attachment_header_file);
                byte[] data = new byte[(int) attachment_header_file.length()];
                fis.read(data);
                fis.close();
                ATTACHMENT_HEADER_WRAPPER = new String(data,"UTF-8");
            } catch (Exception e) {
                throw new Exception("Can't read wrapper file content: wrap-AttachmentHeader.inc", e);
            }
            ATTACHMENT_HEADER_WRAPPER = ATTACHMENT_HEADER_WRAPPER.replace("#FILE_NAME#", teamplate.getAttachment().getFileName());
            ATTACHMENT_HEADER_WRAPPER = ATTACHMENT_HEADER_WRAPPER.replace("#MIME_TYPE#", teamplate.getAttachment().getMimeType());
            ATTACHMENT_HEADER_WRAPPER = ATTACHMENT_HEADER_WRAPPER.replace("#SIGNATURE#", teamplate.getAttachment().getSignature());
            
            ATTACHMENT_HEADER_LIST_WRAPPER = ATTACHMENT_HEADER_LIST_WRAPPER.replace("#ATTACHMENT_HEADER#",ATTACHMENT_HEADER_WRAPPER);

            //AttachmentContentList
            File attachment_content_list_file = new File(this.APP_PATH+"wrap-AttachmentContentList.inc");
            if (!attachment_content_list_file.isFile()) {
                throw new Exception("Wrapper file is not found. Check path to file:\n "+APP_PATH+"wrap-AttachmentContentList.inc");
            }

            try {
                FileInputStream fis = new FileInputStream(attachment_content_list_file);
                byte[] data = new byte[(int) attachment_content_list_file.length()];
                fis.read(data);
                fis.close();
                ATTACHMENT_CONTENT_LIST_WRAPPER = new String(data,"UTF-8");
            } catch (Exception e) {
                throw new Exception("Can't read wrapper file content: wrap-AttachmentContentList.inc", e);
            }

            //AttachmentContent
            String ATTACHMENT_CONTENT_WRAPPER = "";
            File attachment_content_file = new File(this.APP_PATH+"wrap-AttachmentContent.inc");
            if (!attachment_content_file.isFile()) {
                throw new Exception("Wrapper file is not found. Check path to file:\n "+APP_PATH+"wrap-AttachmentContent.inc");
            }
            
            try {
                FileInputStream fis = new FileInputStream(attachment_content_file);
                byte[] data = new byte[(int) attachment_content_file.length()];
                fis.read(data);
                fis.close();
                ATTACHMENT_CONTENT_WRAPPER = new String(data,"UTF-8");
            } catch (Exception e) {
                throw new Exception("Can't read wrapper file content: wrap-AttachmentContent.inc", e);
            }
            ATTACHMENT_CONTENT_WRAPPER = ATTACHMENT_CONTENT_WRAPPER.replace("#FILE_NAME#", teamplate.getAttachment().getFileName());
            ATTACHMENT_CONTENT_WRAPPER = ATTACHMENT_CONTENT_WRAPPER.replace("#CONTENT#", teamplate.getAttachment().getContent());
            
            ATTACHMENT_CONTENT_LIST_WRAPPER = ATTACHMENT_CONTENT_LIST_WRAPPER.replace("#ATTACHMENT_CONTENT#",ATTACHMENT_CONTENT_WRAPPER);
        }
        XML_INPUT = XML_INPUT.replace("#ATTACHMENT_HEADER_LIST#",ATTACHMENT_HEADER_LIST_WRAPPER);
        XML_INPUT = XML_INPUT.replace("#ATTACHMENT_CONTENT_LIST#",ATTACHMENT_CONTENT_LIST_WRAPPER);
        

        // формируем TIMSTAMP и делаем вставку в шаблон
        // пример даты: 2020-01-28T10:09:55.141+03:00
        DateTimeFormatter dtfmt = DateTimeFormatter.ISO_OFFSET_DATE_TIME;
        String TIMESTAMP = dtfmt.format(ZonedDateTime.now());
        XML_INPUT = XML_INPUT.replace("#TIMESTAMP#",TIMESTAMP);
        // заменяем все ентеры и пробелы после них
        // XML_INPUT = TrimXml(XML_INPUT);
        // подписываем и пишем в файл
        try {
            System.out.println("Input xml:\n" + XML_INPUT + "\n");

            SOAPMessage signed = Signer.sign(XML_INPUT.getBytes(UTF_8), new SignAttributes(KEY_ALIAS, KEY_PASS, TAG_FOR_SIGN));
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            signed.writeTo(outputStream);
            XML_OUTPUT = new String(outputStream.toByteArray());

            System.out.println("Output xml:\n" + XML_OUTPUT + "\n");
            // ok
        } catch (Exception e) {
            throw new Exception("Can't sign mesage", e);
        }

        return new SmevMesage(MESSAGE_ID, XML_OUTPUT);
    }

    public byte[] signPkcs7(byte[] data) throws Exception{
        final PrivateKey[] keys = new PrivateKey[1];
        keys[0] = getKey();
        final Certificate[] certs = new Certificate[1];
        certs[0] = getCert();

        return CMSSign.createHashCMS(data, keys, certs, null, true);
    }

	public PrivateKey getKey() throws Exception {
		return getPrivateKey(this.KEY_ALIAS, this.KEY_PASS.toCharArray());
	}

    public Certificate getCert() throws Exception {
		return getCertificate(this.KEY_ALIAS);
	}

    private static String TrimXml(String input) {
        BufferedReader reader = new BufferedReader(new StringReader(input));
        try{
            String str;
            String trimmedXML = "";
            while ( (str = reader.readLine() ) != null){
                String str1 = str;
                if (str1.length()>0)
                    str1 = str1.trim();
                if (str1.length()>0){
                    if(str1.charAt(str1.length()-1) == '>'){
                        trimmedXML = trimmedXML + str.trim();
                    }
                    else{
                        trimmedXML = trimmedXML + str;
                    }
                }
            }
            return trimmedXML;
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    // интерфейс конфигурации для подписания
    static class SignAttributes implements SignAttributesSupplier
    {
        String KEY_ALIAS;
        String KEY_PASS;
        String TAG_FOR_SIGN;

        public SignAttributes(String KEY_ALIAS, String KEY_PASS, String TAG_FOR_SIGN){
            this.KEY_ALIAS = KEY_ALIAS;
            this.KEY_PASS = KEY_PASS;
            this.TAG_FOR_SIGN = TAG_FOR_SIGN;
        }

        @Override public X509Certificate x509Certificate() throws Exception {
            return getX509Certificate(this.KEY_ALIAS);
        }

        @Override public PrivateKey privateKey() throws Exception {
            return getPrivateKey(this.KEY_ALIAS, this.KEY_PASS.toCharArray());
        }

        @Override public String forSignElementId() {
            return this.TAG_FOR_SIGN;
        }
    }
}
