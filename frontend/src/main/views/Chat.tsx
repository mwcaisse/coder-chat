import {
    IconButton,
    Container,
    Stack,
    TextField,
    Paper,
    Box,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { FormEvent, useEffect, useState } from "react";
import remarkGfm from "remark-gfm";
import rehypeStarryNight from "rehype-starry-night";
import { MarkdownHooks } from "react-markdown";

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

export default function Chat() {
    const [chatId, setChatId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [currentMessage, setCurrentMessage] = useState("");

    const [inProcessMessageResponse, setInProcessMessageResponse] = useState<
        string[]
    >([]);

    useEffect(() => {
        if (chatId !== null) {
            return;
        }

        // otherwise we shall fetch a (rug) chat id
        const getChatId = async () => {
            const resp = await fetch("/api/chat/", {
                method: "POST",
                headers: {
                    Accept: "application/json",
                },
            });
            const data = await resp.json();
            setChatId(data.id);
            console.log("Created a chat with id: ", data.id);
        };
        getChatId();
    }, [chatId]);

    const obSubmit = (event: FormEvent<HTMLFormElement>) => {
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
        const resp = await fetch(`/api/chat/${chatId}/message`, {
            method: "POST",
            body: JSON.stringify({ message: message }),
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
        });

        let responseMessage = "";
        const stringReader = resp.body.pipeThrough(new TextDecoderStream());
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
    };

    return (
        <Container sx={{ pt: 2 }}>
            <Stack direction="column" spacing={2}>
                <Stack direction="column" spacing={1}>
                    {messages.map((message, index) => (
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
                </Stack>
                <form onSubmit={obSubmit}>
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
                            onChange={(e) => setCurrentMessage(e.target.value)}
                        />
                        <IconButton size="large" type="submit">
                            <SendIcon />
                        </IconButton>
                    </Stack>
                </form>
            </Stack>
        </Container>
    );
}
