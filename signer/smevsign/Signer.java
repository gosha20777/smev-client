package smevsign;

import static smevsign.Resources.CALLER_INFORMATION_SYSTEM_SIGNATURE;
import static smevsign.Resources.CANONICALIZATION_METHOD;
import static smevsign.Resources.SMEV_TRANSFORM_URN;
import static smevsign.Resources.XMLDSIG_MORE_GOSTR34102001_GOSTR3411;
import static smevsign.Resources.XMLDSIG_MORE_GOSTR3411;

import javax.xml.soap.SOAPMessage;

import org.apache.xml.security.exceptions.AlgorithmAlreadyRegisteredException;
import org.apache.xml.security.signature.XMLSignature;
import org.apache.xml.security.transforms.Transform;
import org.apache.xml.security.transforms.TransformationException;
import org.apache.xml.security.transforms.Transforms;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

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

public class Signer {
    private static boolean isInit;

    private static void init(){
        //Для соответствия требованиям методических рекомендаций 3.4
        System.setProperty("org.apache.xml.security.ignoreLineBreaks", "true");
        //Обязательная инициализация для распознавания ГОСТа
        ru.CryptoPro.JCPxml.xmldsig.JCPXMLDSigInit.init(); 
        try {
            //Регистрация дополнительной трансформации
            Transform.register(SMEV_TRANSFORM_URN, SmevTransformSpi.class.getName());
        } catch (AlgorithmAlreadyRegisteredException ignored) {
            //Алгоритм уже зарегистрирован
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException(e);
        }
        isInit = true;
    }

    /**Подписывает XML в виде массива байтов в соответствиями с требованиями методических рекомендаций СМЭВ 3.4.0.3
     * Возвращает готовое к отправке в СМЭВ SOAP сообщение*/
    public static SOAPMessage sign(byte[] forSignData, SignAttributesSupplier attrSupplier) throws Exception {
        if (!isInit) init();

        Document forSign = Converters.byteArrayToW3cDoc(forSignData);

        //инициализация объекта формирования ЭЦП в соответствии с ГОСТ Р 34.10-2001
        XMLSignature signature = new XMLSignature(forSign, "", XMLDSIG_MORE_GOSTR34102001_GOSTR3411, CANONICALIZATION_METHOD);

        addSignatureNode(forSign, signature);

        //Добавление узла <ds:Reference> для обработки XML в соответствии с заданным алгоритмом хеширования и правилами из <ds:Transforms>
        signature.addDocument("#" + attrSupplier.forSignElementId(), createTransformationNode(forSign), XMLDSIG_MORE_GOSTR3411);

        //создание узла <ds:KeyInfo> - информации об открытом ключе на основе сертификата
        signature.addKeyInfo(attrSupplier.x509Certificate());
        
        //создание подписи XML-документа на основе ключа и заднных правил
        signature.sign(attrSupplier.privateKey());

        return Converters.documentToSoap(forSign);
    }

    /**Cоздание узла преобразований <ds:Transforms> и добавление в него правил работы с документом */
    private static Transforms createTransformationNode(Document doc) throws TransformationException {
        Transforms transforms = new Transforms(doc);
        transforms.addTransform(Transforms.TRANSFORM_C14N_EXCL_OMIT_COMMENTS);
        transforms.addTransform(SMEV_TRANSFORM_URN);
        return transforms;
    }

    /**Добавление узла <ds:Signature> в XML*/
    private static void addSignatureNode(Document doc, XMLSignature sig){
        //Получение узла XML-документа для добавления узла подписи
        Element element = (Element)doc.getElementsByTagNameNS("*", CALLER_INFORMATION_SYSTEM_SIGNATURE).item(0);

        //Добавление узла подписи
        if (element == null) throw new RuntimeException("Не найдено место для подписи: " + CALLER_INFORMATION_SYSTEM_SIGNATURE);
        element.appendChild(sig.getElement());
    }
}