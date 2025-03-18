import { redirect, type Handle } from '@sveltejs/kit';

// Define the paths that are unprotected (can be accessed without authentication)

export const handle: Handle = async ({ event, resolve }) => {
    console.log('Hook is running');

    const session = event.cookies.get('session'); // Check for a session cookie
    const currentPath = event.url.pathname;
    console.log('Current path:', currentPath);

    // Log if the session is present
    console.log('Session:', session);

    try {
        // Attempt to fetch user details if session exists
        if (session) {
            const requestOptions = {
                method: "GET",
                redirect: "follow"
              };
              
            const url = (
                'http://127.0.0.1:8000/user/get_user_details?' +
                new URLSearchParams({ user_id: session as string }).toString()
            );

            const response = await fetch(url, requestOptions);

            if (!response.ok) {
                console.error('Failed to fetch user details:', response.statusText);
                event.cookies.delete('session', { path: '/' });
                return redirect(303, '/login');
            }

            const { success, first_name, last_name } = await response.json();

            if (success) {
                event.locals.user = {
                    isAuthenticated: true,
                    first_name: first_name,
                    last_name: last_name,
                    id: session,
                };
                console.log('User details fetched successfully:', event.locals.user);
            } else {
                console.log('Invalid session, redirecting to login');
                return redirect(303, '/login');
            }
        }
    } catch (error) {
        console.error('Error during user detail fetch:', error);
        return redirect(303, '/login');
    }

    // Allow the request to proceed if it passes the checks
    const response = await resolve(event)

    return response
};
