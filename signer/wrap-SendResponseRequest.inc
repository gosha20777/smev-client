<ns:SendResponseRequest xmlns:ns="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.1" xmlns:ns1="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.1">
    <ns:SenderProvidedResponseData Id="SIGNED_BY_CONSUMER" xmlns:ns="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.1" xmlns:ns1="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.1">
        <ns:MessageID>#MESSAGE_ID#</ns:MessageID>
        <ns:To>#TO#</ns:To>
        <ns1:MessagePrimaryContent>#REQUEST_BODY#</ns1:MessagePrimaryContent>
    </ns:SenderProvidedResponseData>
    <ns:CallerInformationSystemSignature></ns:CallerInformationSystemSignature>
</ns:SendResponseRequest>