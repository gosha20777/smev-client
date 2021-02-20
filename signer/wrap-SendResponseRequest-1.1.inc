<ns2:SendResponseRequest xmlns="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.1" xmlns:ns2="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.1">
    <ns2:SenderProvidedResponseData Id="SIGNED_BY_CONSUMER">
        <ns2:MessageID>#MESSAGE_ID#</ns2:MessageID>
        <ns2:To>#TO#</ns2:To>
        <ns3:MessagePrimaryContent xmlns:ns3="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.1">#REQUEST_BODY#</ns3:MessagePrimaryContent>
        #ATTACHMENT_HEADER_LIST#
    </ns2:SenderProvidedResponseData>
    #ATTACHMENT_CONTENT_LIST#
    <ns2:CallerInformationSystemSignature></ns2:CallerInformationSystemSignature>
</ns2:SendResponseRequest>