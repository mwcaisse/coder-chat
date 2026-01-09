import {
    IconButton,
    Container,
    Stack,
    TextField,
    Paper,
    Box,
    CircularProgress,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { FormEvent, memo, useLayoutEffect, useRef, useState } from "react";
import remarkGfm from "remark-gfm";
import rehypeStarryNight from "rehype-starry-night";
import { MarkdownHooks } from "react-markdown";
import { useAuthStore } from "@app/stores/AuthenticationStore.ts";

type Message = {
    content: string;
    user: boolean;
};

type ChatMessageProps = {
    content: string;
};

type Chat = {
    id: string;
    name: string;
    language?: string;
};

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

const ChatMessage = memo(function ChatMessage({ content }: ChatMessageProps) {
    return (
        <Paper
            sx={{
                px: 2,
                borderRadius: 5,
            }}
        >
            <MarkdownHooks
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeStarryNight]}
            >
                {content}
            </MarkdownHooks>
        </Paper>
    );
});

function ChatMessageLoading() {
    return (
        <Paper
            sx={{
                p: 2,
                borderRadius: 5,
            }}
        >
            <CircularProgress />
        </Paper>
    );
}

type EmptyChatPromptProps = {
    onSubmit: (event: FormEvent<HTMLFormElement>) => void;
    currentMessage: string;
    setCurrentMessage: (message: string) => void;
};

function EmptyChatPrompt({
    onSubmit,
    currentMessage,
    setCurrentMessage,
}: EmptyChatPromptProps) {
    return (
        <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            sx={{ height: "100vh" }}
        >
            <form onSubmit={onSubmit}>
                <Stack direction="row" spacing={1}>
                    <TextField
                        variant="outlined"
                        fullWidth
                        sx={{
                            minWidth: "60vw",
                        }}
                        slotProps={{
                            input: {
                                sx: { borderRadius: 5 },
                            },
                        }}
                        placeholder="Ask coder chat"
                        value={currentMessage}
                        onChange={(e) => setCurrentMessage(e.target.value)}
                    />
                    <IconButton size="large" type="submit">
                        <SendIcon />
                    </IconButton>
                </Stack>
            </form>
        </Box>
    );
}

export default function Chat() {
    const authToken = useAuthStore((state) => state.authToken);
    const [chatId, setChatId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [currentMessage, setCurrentMessage] = useState("");

    const [loadingMessageResponse, setLoadingMessageResponse] = useState(false);
    const [inProcessMessageResponse, setInProcessMessageResponse] = useState<
        string[]
    >([]);

    const chatBoxRef = useRef<HTMLDivElement>(null);
    const [chatBoxHeight, setChatBoxHeight] = useState<number>(100);

    useLayoutEffect(() => {
        const updateHeight = () => {
            if (chatBoxRef.current) {
                const { height } = chatBoxRef.current.getBoundingClientRect();
                setChatBoxHeight(height);
            }
        };

        updateHeight();

        window.addEventListener("resize", updateHeight);

        return () => window.removeEventListener("resize", updateHeight);
    }, []);

    const onSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        if (currentMessage.length === 0) return;
        setMessages((prev) => [
            ...prev,
            { user: true, content: currentMessage },
        ]);
        sendMessage(currentMessage);
        setCurrentMessage("");
    };

    const sendMessage = async (message: string) => {
        setLoadingMessageResponse(true);

        // depending on whether we have a chat id already, we will call a different endpoint, either:
        //  - create a chat + send a message
        //  - send a message to an existing chat

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
            { user: false, content: responseMessage },
        ]);
        setInProcessMessageResponse([]);
        setLoadingMessageResponse(false);
    };

    return (
        <Container sx={{ pt: 2 }}>
            {messages.length === 0 && (
                <EmptyChatPrompt
                    currentMessage={currentMessage}
                    setCurrentMessage={setCurrentMessage}
                    onSubmit={onSubmit}
                />
            )}
            {messages.length !== 0 && (
                <Box flexGrow={1}>
                    <Stack
                        direction="column-reverse"
                        spacing={1}
                        sx={{
                            height: `calc(100vh - ${chatBoxHeight + 40}px)`,
                            overflowY: "auto",
                        }}
                    >
                        {loadingMessageResponse &&
                            inProcessMessageResponse.length === 0 && (
                                <Box
                                    sx={{
                                        display: "flex",
                                        flexDirection: "row",
                                        justifyContent: "flex-start",
                                        maxWidth: "100%",
                                    }}
                                >
                                    <ChatMessageLoading />
                                </Box>
                            )}
                        {inProcessMessageResponse.length > 0 && (
                            <Box
                                sx={{
                                    display: "flex",
                                    flexDirection: "row",
                                    justifyContent: "flex-start",
                                    maxWidth: "100%",
                                }}
                            >
                                <ChatMessage
                                    content={inProcessMessageResponse.join("")}
                                />
                            </Box>
                        )}
                        {messages
                            .slice()
                            .reverse()
                            .map((message, index) => (
                                <Box
                                    key={index}
                                    sx={{
                                        display: "flex",
                                        flexDirection: "row",
                                        justifyContent: message.user
                                            ? "flex-end"
                                            : "flex-start",
                                        maxWidth: "100%",
                                    }}
                                >
                                    <ChatMessage content={message.content} />
                                </Box>
                            ))}
                    </Stack>
                    <Box
                        sx={{
                            position: "fixed",
                            bottom: 10,
                            width: "100%",
                            maxWidth: "lg",
                        }}
                        ref={chatBoxRef}
                    >
                        <form onSubmit={onSubmit}>
                            <Stack direction="row" spacing={1}>
                                <TextField
                                    variant="outlined"
                                    fullWidth
                                    slotProps={{
                                        input: {
                                            sx: { borderRadius: 5 },
                                        },
                                    }}
                                    placeholder="Ask coder chat"
                                    value={currentMessage}
                                    onChange={(e) =>
                                        setCurrentMessage(e.target.value)
                                    }
                                />
                                <IconButton size="large" type="submit">
                                    <SendIcon />
                                </IconButton>
                            </Stack>
                        </form>
                    </Box>
                </Box>
            )}
        </Container>
    );
}
