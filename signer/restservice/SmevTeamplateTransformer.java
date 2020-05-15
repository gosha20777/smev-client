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
import javax.xml.soap.SOAPMessage;
import com.fasterxml.uuid.Generators;
import static java.nio.charset.StandardCharsets.UTF_8;
import static smevsign.KeyStoreWrapper.getPrivateKey;
import static smevsign.KeyStoreWrapper.getX509Certificate;
import smevsign.SignAttributesSupplier;
import smevsign.Signer;
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
    
    public SmevMesage Transform(SmevTeamplate teamplate) throws Exception {
        String XML_WRAPPER = "";
        String ATTACHMENT_WRAPPER = "";
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
        File wrapper_file = new File(this.APP_PATH+"wrap-"+MSG_TYPE+".inc");
        if (!wrapper_file.isFile()) {
            throw new Exception("Wrapper file is not found for this MSG_TYPE. Check path to file or MSG_TYPE:\n "+APP_PATH+"wrap-"+MSG_TYPE+".inc");
        }

        try {
            FileInputStream fis = new FileInputStream(wrapper_file);
            byte[] data = new byte[(int) wrapper_file.length()];
            fis.read(data);
            fis.close();
            XML_WRAPPER = new String(data,"UTF-8");
        } catch (Exception e) {
            throw new Exception("Can't read wrapper file content: "+APP_PATH+"wrap-"+MSG_TYPE+".inc", e);
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

        /*
        if(teamplate.getAttachment() != null){
            File attachment_wrapper_file = new File(this.APP_PATH+"wrap-Attachment.inc");
            if (!attachment_wrapper_file.isFile()) {
                throw new Exception("Wrapper file is not found for this MSG_TYPE. Check path to file or MSG_TYPE:\n "+APP_PATH+"wrap-"+MSG_TYPE+".inc");
            }

            try {
                FileInputStream fis = new FileInputStream(attachment_wrapper_file);
                byte[] data = new byte[(int) attachment_wrapper_file.length()];
                fis.read(data);
                fis.close();
                ATTACHMENT_WRAPPER = new String(data,"UTF-8");
            } catch (Exception e) {
                throw new Exception("Can't read wrapper file content: wrap-Attachment.inc", e);
            }

            ATTACHMENT_WRAPPER = ATTACHMENT_WRAPPER.replace("#MESSAGE_ID#",MESSAGE_ID);
            ATTACHMENT_WRAPPER = ATTACHMENT_WRAPPER.replace("#FILE_HASH#",teamplate.getAttachment().getHash());
            ATTACHMENT_WRAPPER = ATTACHMENT_WRAPPER.replace("#FILE_TYPE#",teamplate.getAttachment().getMimeType());
            ATTACHMENT_WRAPPER = ATTACHMENT_WRAPPER.replace("#PKS7#",teamplate.getAttachment().getSignature());
        }

        XML_INPUT = XML_INPUT.replace("#ATTACHMENT_BLOCK#",ATTACHMENT_WRAPPER);
        System.out.println("#ATTACHMENT_BLOCK# "+ ATTACHMENT_WRAPPER);
        */

        // вставляем To в шаблон если это надо
        if (MSG_TYPE.equals("SendResponseRequest")){
            XML_INPUT = XML_INPUT.replace("#TO#",teamplate.getTo());
	        System.out.println("replace");
        }

        // формируем TIMSTAMP и делаем вставку в шаблон
        // пример даты: 2020-01-28T10:09:55.141+03:00
        DateTimeFormatter dtfmt = DateTimeFormatter.ISO_OFFSET_DATE_TIME;
        String TIMESTAMP = dtfmt.format(ZonedDateTime.now());
        XML_INPUT = XML_INPUT.replace("#TIMESTAMP#",TIMESTAMP);
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
