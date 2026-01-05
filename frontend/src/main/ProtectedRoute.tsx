import { useAuthStore } from "@app/stores/AuthenticationStore.ts";
import { useNavigate } from "react-router";
import { useEffect } from "react";
import { jwtDecode } from "jwt-decode";

function authTokenValid(token: string | null): boolean {
    if (token === null || token.length === 0) {
        return false;
    }

    const payload = jwtDecode(token);
    if (payload.exp === undefined) {
        return false;
    }
    // token is valid if the expiration date is in the future
    return Date.now() < payload.exp * 1000;
}

export function ProtectedRoute({ children }: React.PropsWithChildren) {
    const authToken = useAuthStore((state) => state.authToken);
    const navigate = useNavigate();

    useEffect(() => {
        // if auth token is invalid, redirect to login page
        // TODO: Update this to use refresh token in future
        if (!authTokenValid(authToken)) {
            navigate("/login");
        }
    }, [authToken]);

    return children;
}

interface UnauthedRouteProps extends React.PropsWithChildren {
    redirectTo?: string;
}

export function UnauthedRoute({
    children,
    redirectTo = "/",
}: UnauthedRouteProps) {
    const authToken = useAuthStore((state) => state.authToken);
    const navigate = useNavigate();

    useEffect(() => {
        // if we have a valid auth token, then redirect to home page
        if (authTokenValid(authToken)) {
            navigate(redirectTo);
        }
    }, [authToken]);

    return children;
}
