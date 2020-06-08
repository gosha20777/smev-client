<ns3:SendRequestRequest xmlns="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/basic/1.1"
    xmlns:ns2="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/faults/1.1"
    xmlns:ns3="urn://x-artefacts-smev-gov-ru/services/message-exchange/types/1.1">
    <ns3:SenderProvidedRequestData Id="SIGNED_BY_CONSUMER">
        <ns3:MessageID>#MESSAGE_ID#</ns3:MessageID>
        <ns3:NodeID></ns3:NodeID>
        <MessagePrimaryContent>
            #REQUEST_BODY#
        </MessagePrimaryContent>
        #ATTACHMENT_HEADER_LIST#
        <ns3:BusinessProcessMetadata/>
    </ns3:SenderProvidedRequestData>
    #ATTACHMENT_CONTENT_LIST#
    <ns3:CallerInformationSystemSignature></ns3:CallerInformationSystemSignature>
</ns3:SendRequestRequest>