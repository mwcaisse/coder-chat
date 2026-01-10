import { createContext, useContext, useState } from "react";
import { useAuthStore } from "@app/stores/AuthenticationStore.ts";
import { Chat, Message } from "@app/components/ChatTypes.ts";

type CreateChatResponse = {
    chat: Chat;
    messageStream: AsyncGenerator<string, void, void>;
};

/**
 *
 * @param stream_reader
 * @param current_chunk Any left over parts of the last chunk of the stream read, this will be immediately yielded
 */
async function* messageStreamGenerator(
    stream_reader: ReadableStreamDefaultReader,
    current_chunk: string | null,
) {
    if (current_chunk !== null) {
        yield current_chunk;
    }
    try {
        while (true) {
            const { done, value } = await stream_reader.read();
            if (done) {
                return;
            }
            yield value;
        }
    } finally {
        stream_reader.releaseLock();
    }
}

async function createChatAndSendMessage(
    message: string,
    authToken: string,
): Promise<CreateChatResponse> {
    const resp = await fetch(`/api/chat/message`, {
        method: "POST",
        body: JSON.stringify({ message: message }),
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: `Bearer ${authToken}`,
        },
    });

    // check if we received a non-successful response and throw an error in that case
    if (!resp.ok) {
        // TODO: Better error here, but this work for now
        throw new Error("Failed to send message");
    }

    const bodyStreamReader = resp
        .body!.pipeThrough(new TextDecoderStream())
        .getReader();

    let buffer = "";
    let remainder: string | null = null;
    try {
        while (true) {
            const { done, value } = await bodyStreamReader.read();
            if (done) {
                throw new Error(
                    "Could not parse create chat and message response. Did not find chat JSON",
                );
            }
            if (value.indexOf("\n") !== -1) {
                buffer += value.slice(0, value.indexOf("\n"));
                remainder = value.slice(value.indexOf("\n") + 1);
                break;
            } else {
                buffer += value;
            }
        }
    } catch (e) {
        bodyStreamReader.releaseLock();
        throw e;
    }

    return {
        chat: JSON.parse(buffer) as Chat,
        messageStream: messageStreamGenerator(bodyStreamReader, remainder),
    };
}

async function sendMessageApi(
    chatId: string,
    message: string,
    authToken: string,
) {
    const resp = await fetch(`/api/chat/${chatId}/message`, {
        method: "POST",
        body: JSON.stringify({ message: message }),
        headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            Authorization: `Bearer ${authToken}`,
        },
    });

    // check if we received a non-successful response and throw an error in that case
    if (!resp.ok) {
        // TODO: Better error here, but this work for now
        throw new Error("Failed to send message");
    }

    // the whole body will be the response message, so return that directly
    return resp.body!.pipeThrough(new TextDecoderStream());
}

type ChatContextObject = {
    chatId: string | null;
    messages: Message[];
    loadingMessageResponse: boolean;
    inProcessMessageResponse: string[];
    sendMessage: (message: string) => Promise<void>;
    newChat: () => void;
};

export const ChatContext = createContext<ChatContextObject>(null!);

export const ChatContextProvider = ({ children }: React.PropsWithChildren) => {
    const authToken = useAuthStore((state) => state.authToken);

    const [chatId, setChatId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);

    const [loadingMessageResponse, setLoadingMessageResponse] = useState(false);
    const [inProcessMessageResponse, setInProcessMessageResponse] = useState<
        string[]
    >([]);

    // Posts a new user message to the chat
    const sendMessage = async (message: string) => {
        setMessages((prev) => [...prev, { content: message, from_user: true }]);
        setLoadingMessageResponse(true);

        let responseMessage = "";
        let messageStream;
        if (chatId === null) {
            const { chat, messageStream: ms } = await createChatAndSendMessage(
                message,
                authToken!,
            );
            setChatId(chat.id);
            messageStream = ms;
        } else {
            messageStream = await sendMessageApi(chatId, message, authToken!);
        }

        // @ts-expect-error ReadableStream is an iterator, despite what the typing says
        for await (const chunk of messageStream) {
            setInProcessMessageResponse((prev) => [...prev, chunk]);
            responseMessage += chunk;
        }

        // once we've finished reading the whole body, remove it from the in progress message and make it a real message
        setMessages((prev) => [
            ...prev,
            { from_user: false, content: responseMessage },
        ]);
        setInProcessMessageResponse([]);
        setLoadingMessageResponse(false);
    };

    const newChat = () => {
        setChatId(null);
        setMessages([]);
        // TODO: Might want to cancel any in progress message responses here as well
        setInProcessMessageResponse([]);
    };

    const contextValue: ChatContextObject = {
        chatId,
        messages,
        loadingMessageResponse,
        inProcessMessageResponse,
        sendMessage,
        newChat,
    };

    return <ChatContext value={contextValue}>{children}</ChatContext>;
};

export const useChatContext = () => {
    const context = useContext(ChatContext);
    if (!context) {
        throw new Error(
            "useChatContext must be used within a ChatContextProvider",
        );
    }
    return context;
};
