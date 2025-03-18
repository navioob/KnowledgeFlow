import { redirect } from "@sveltejs/kit";
import type {PageServerLoad } from "./$types";

export const load: PageServerLoad = async ({ locals }) => {
    console.log(locals)

    //redirect to login if there's no session key
    if (!locals.user){
        throw redirect(303, '/login')
    }


    let documentList = [];

    //get document list
    const requestOptions = {
        method: "GET",
        redirect: "follow"
      };
      
    const url = (
        'http://127.0.0.1:8000/document/list?' +
        new URLSearchParams({ user_id: locals.user.id}).toString()
    );

    try {
        const res = await fetch(url, requestOptions);
        if (!res.ok) throw new Error('Failed to fetch documents');
        let response = await res.json();
        documentList = response.content
        console.log(documentList)
    } catch (error) {
        console.error('Error fetching documents:', error);
    }

    
    return {
        user: locals.user, // Pass user data to the client
        documentList : documentList
    };
}

