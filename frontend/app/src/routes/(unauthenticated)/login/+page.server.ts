import { redirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
// Import forge library
import forge from 'node-forge';
import { dev } from '$app/environment';
import fs from 'fs';
import path from 'path';

export const actions = {
    Login: async ({ request, cookies }) => {
        const form = await request.formData();
        const username = form.get('username');
        const password = form.get('password');

        // Define the path to the private folder where you store your .pem file
        const publicKeyPath = path.join(process.cwd(), 'private', 'keys', 'public.pem');

        // Read the .pem file
        let publicKey;
        try {
            publicKey = fs.readFileSync(publicKeyPath, 'utf8');
        } catch (err) {
            console.error('Error reading the public key:', err);
            return { success: false, error: 'Failed to read the public key.' };
        }

        console.log('Submitting the Login form...');
        console.log('Username:', username);
        console.log('Password (before encryption):', password);

        // Use forge to convert the PEM public key to a usable RSA public key object
        const rsa = forge.pki.publicKeyFromPem(publicKey);

        console.log('Public Key:', publicKey);

        // Encrypt the password with the public key
        const encryptedPassword = forge.util.encode64(rsa.encrypt(password, 'RSAES-PKCS1-V1_5'));

        console.log('Encrypted Password:', encryptedPassword);

        console.log(
            'Payload',
            JSON.stringify({
                username: username,
                password: encryptedPassword
            })
        );

        // Send the form data with the encrypted password to the backend
        const response = await fetch('http://127.0.0.1:8000/user/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: encryptedPassword
            })
        });
        const { success, message, user_id } = await response.json();

        console.log(success, message, user_id)

        //set user session cookies
        if(success)
            cookies.set('session', user_id, {
                path: '/',
                httpOnly: true,
                sameSite: 'strict',
                secure: !dev,
                maxAge: 60 * 60 * 24 * 30
            });
        return{
            success:success,
            message:message
        }
    }
} satisfies Actions;

export const load: PageServerLoad = async ({ locals }) => {
    console.log(locals)

    if (locals.user){
        throw redirect(303, '/home')
    }
}

