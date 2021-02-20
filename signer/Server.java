import static spark.Spark.*;
import java.security.PrivateKey;
import java.security.cert.Certificate;
import java.util.Base64;
import java.io.File;
import java.io.FileInputStream;
import java.util.HashMap;
import java.util.Map;
import restservice.*;
import smevsign.*;

import com.google.gson.Gson;
//import org.apache.log4j.Logger;

public class Server {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Error. Not enough input params in arguments line.\n\nUsage:\n java -classpath . Server <port> <cingig.json>");
            System.exit(0);
        }

        port(Integer.parseInt(args[0]));

        org.slf4j.Logger LOG = org.slf4j.LoggerFactory.getLogger("main");
        try {
            //Load config.json
            CertRepository repo;
            try {
                File input_file = new File(args[1]);
                FileInputStream fis = new FileInputStream(input_file);
                byte[] data = new byte[(int) input_file.length()];
                fis.read(data);
                fis.close();
                repo = new Gson().fromJson(new String(data, "UTF-8"), CertRepository.class);
            } catch (Exception e) {
                throw new Exception("Can't read input file content: " + args[1]);
            }

            Map<String, SmevTeamplateTransformer> transformers = new HashMap<String, SmevTeamplateTransformer>();

            for (String key : repo.getCerts().keySet()) {
                transformers.put(key, new SmevTeamplateTransformer(repo.getCerts().get(key).getAlias(), repo.getCerts().get(key).getPassword()));
            }

            LOG.info(String.format("Application is started at port %s", args[0]));

            post("/api/v1/message/:alias", (request, response) -> {
                try {
                    String shemeType = request.queryParams("type");
                    shemeType = shemeType != null ? shemeType : "1.2";
                    if (!shemeType.equals("1.1") &
                        !shemeType.equals("1.2")){
                        throw new Exception("Invalid input: type - `" + shemeType + "`");
                    }

                    SmevTeamplate teamplate = new Gson().fromJson(request.body(), restservice.SmevTeamplate.class);
                    if (teamplate == null){
                        throw new Exception("Invalid input: null");
                    }
                    if (teamplate.getId() == null || teamplate.getId().length() < 1){
                        throw new Exception("Invalid input: id");
                    }
                    if (teamplate.getXml() == null){
                        teamplate.setXml("");
                    }
                    if (teamplate.getMsgType() == null){
                        throw new Exception("Invalid input: msgType - `null`");
                    }
                    if (!teamplate.getMsgType().equals("SendRequestRequest") &
                        !teamplate.getMsgType().equals("GetResponseRequest") &
                        !teamplate.getMsgType().equals("GetRequestRequest") &
                        !teamplate.getMsgType().equals("SendResponseRequest") &
                        !teamplate.getMsgType().equals("GetIncomingQueueStatisticsRequest") &
                        !teamplate.getMsgType().equals("AckRequest")){
                        throw new Exception("Invalid input: msgType - `" + teamplate.getMsgType() + "`");
                    }
                    if (teamplate.getTo() == null & teamplate.getMsgType().equals("SendResponseRequest")){
                        throw new Exception("Invalid input: getTo - `null`");
                    }
                    if (teamplate.getTagForSign() == null){
                        throw new Exception("Invalid input: tagForSign - `null`");
                    }
                    if (!teamplate.getTagForSign().equals("SIGNED_BY_CALLER") &
                        !teamplate.getTagForSign().equals("SIGNED_BY_CONSUMER")){
                        throw new Exception("Invalid input: tagForSign - `" + teamplate.getTagForSign() + "`");
                    }
                    
                    if(!transformers.containsKey(request.params(":alias")))
                        throw new Exception("Invalid input: alias - `" + request.params(":alias")+ "`");

                    SmevMesage msg = transformers.get(request.params(":alias")).Transform(teamplate, shemeType);
                    response.type("application/json");
                    response.status(200);
                    LOG.info(String.format("%s %s %s", request.requestMethod(), request.url(), response.status()));
                    return new Gson().toJson(msg);
                } catch (Exception e) {
		    e.printStackTrace();				
                    response.type("application/json");
                    response.status(500);
                    LOG.info(String.format("%s %s %s", request.requestMethod(), request.url(), response.status()));
                    return "{ \"error\": \"" + e.getMessage() + "\"}";
                }
            });

            post("/api/v1/pkcs7/:alias", (request, response) -> {
                try {
                    byte[] data = Base64.getDecoder().decode(new String(request.body()).getBytes("UTF-8"));
                    byte[] p7_data = transformers.get(request.params(":alias")).signPkcs7(data);
                    byte[] encoded = Base64.getEncoder().encode(p7_data);
                    return new String(encoded);

                } catch (Exception e) {
                    response.type("application/json");
                    response.status(500);
                    LOG.info(String.format("%s %s %s", request.requestMethod(), request.url(), response.status()));
                    return "{ \"error\": \"" + e.getMessage() + "\"}";
                }
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
