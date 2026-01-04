import { createContext, useContext } from "react";
import { OptionsWithExtraProps, useSnackbar } from "notistack";

type ToastKey = string | number;

type ToastContextObject = {
    showSuccess: (message: string) => ToastKey;
    showError: (message: string) => ToastKey;
};

const ToastContext = createContext<ToastContextObject>(null!);

export const ToastContextProvider = ({ children }: React.PropsWithChildren) => {
    const { enqueueSnackbar } = useSnackbar();

    const commonProps = {
        anchorOrigin: {
            vertical: "top",
            horizontal: "right",
        },
    } as OptionsWithExtraProps<any>;

    const contextObject = {
        showSuccess: (message: string) =>
            enqueueSnackbar(message, { ...commonProps, variant: "success" }),
        showError: (message: string) =>
            enqueueSnackbar(message, { ...commonProps, variant: "error" }),
    };

    return <ToastContext value={contextObject}>{children}</ToastContext>;
};

export const useToastContext = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error(
            "useToastContext must be used within a ToastContextProvider",
        );
    }
    return context;
};
