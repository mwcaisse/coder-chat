import { Box, Drawer, IconButton, Tooltip, Typography } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import CreateIcon from "@mui/icons-material/Create";
import { useState } from "react";
import { useChatContext } from "@app/components/ChatContext.tsx";

export default function ChatLeftMenu() {
    const { newChat } = useChatContext();

    const [expanded, setExpanded] = useState(false);

    const drawerWidth = expanded ? 240 : 60;

    return (
        <Drawer
            open={true}
            variant="persistent"
            sx={{
                width: drawerWidth,
                "& .MuiDrawer-paper": {
                    width: drawerWidth,
                    boxSizing: "border-box",
                },
            }}
        >
            <Box sx={{ p: 1 }}>
                <Tooltip title={expanded ? "Collapse" : "Expand"}>
                    <IconButton onClick={() => setExpanded(!expanded)}>
                        <MenuIcon />
                    </IconButton>
                </Tooltip>
            </Box>
            <Box sx={{ pt: 2 }}></Box>
            <Box sx={{ p: 1 }}>
                <Box
                    sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        direction: "row",
                    }}
                >
                    <Tooltip title="New Chat">
                        <IconButton onClick={() => newChat()}>
                            <CreateIcon />
                        </IconButton>
                    </Tooltip>
                    {expanded && <Typography>New Chat</Typography>}
                </Box>
            </Box>
        </Drawer>
    );
}
