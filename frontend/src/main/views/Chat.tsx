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
import { FormEvent, useEffect, useLayoutEffect, useRef, useState } from "react";
import remarkGfm from "remark-gfm";
import rehypeStarryNight from "rehype-starry-night";
import { MarkdownHooks } from "react-markdown";
import { useAuthStore } from "@app/stores/AuthenticationStore.ts";
import ky from "ky";

type Message = {
    content: string;
    user: boolean;
};

type ChatMessageProps = {
    content: string;
};

function ChatMessage({ content }: ChatMessageProps) {
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
}

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

    useEffect(() => {
        if (authToken === null || chatId !== null) {
            return;
        }

        // otherwise we shall fetch a (rug) chat id
        const getChatId = async () => {
            const data: { id: string } = await ky
                .post("/api/chat/", {
                    headers: {
                        Accept: "application/json",
                        Authorization: `Bearer ${authToken}`,
                    },
                })
                .json();

            setChatId(data.id);
            console.log("Created a chat with id: ", data.id);
        };
        getChatId();
    }, [authToken, chatId]);

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
        const resp = await fetch(`/api/chat/${chatId}/message`, {
            method: "POST",
            body: JSON.stringify({ message: message }),
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                Authorization: `Bearer ${authToken}`,
            },
        });

        let responseMessage = "";
        const stringReader = resp.body!.pipeThrough(new TextDecoderStream());
        // @ts-expect-error the typing of this is weird
        for await (const chunk of stringReader) {
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
