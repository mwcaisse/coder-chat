import { memo } from "react";
import { CircularProgress, Paper } from "@mui/material";
import { MarkdownHooks } from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeStarryNight from "rehype-starry-night";

type ChatMessageProps = {
    content: string;
};

export const ChatMessage = memo(function ChatMessage({
    content,
}: ChatMessageProps) {
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

export function ChatMessageLoading() {
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
