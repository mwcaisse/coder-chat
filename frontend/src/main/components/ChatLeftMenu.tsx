import { Box, Drawer, IconButton, Tooltip } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import CreateIcon from "@mui/icons-material/Create";

export default function ChatLeftMenu() {
    return (
        <Drawer variant="permanent">
            <Box sx={{ p: 1 }}>
                <Tooltip title="Expand">
                    <IconButton>
                        <MenuIcon />
                    </IconButton>
                </Tooltip>
            </Box>
            <Box sx={{ pt: 2 }}></Box>
            <Box sx={{ p: 1 }}>
                <Tooltip title="New Chat">
                    <IconButton>
                        <CreateIcon />
                    </IconButton>
                </Tooltip>
            </Box>
        </Drawer>
    );
}
