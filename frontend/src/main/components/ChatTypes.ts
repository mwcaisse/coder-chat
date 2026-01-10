export type Message = {
    content: string;
    from_user: boolean;
};

export type Chat = {
    id: string;
    name: string;
    language?: string;
    create_date?: string;
};

export type ChatWithMessages = Chat & { messages: Message[] };
