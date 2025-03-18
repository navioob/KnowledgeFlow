import { redirect } from '@sveltejs/kit';

//delete the cookies and reload the same path
export function GET({ cookies }) {
    cookies.delete('session', { path: '/' });
    throw redirect(303, '/');
}