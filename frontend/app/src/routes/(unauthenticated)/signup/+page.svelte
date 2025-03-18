<script lang="ts">
    import type {ActionData } from './$types';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

	/** @type {import('./$types').ActionData} */
	export let form: ActionData;

    let username = '';
    let firstName = '';
    let lastName = '';
    let password = '';



    // Trigger the redirect when the form is successful
    onMount(async () => {
        if (form?.success) {
            await delay(3000); // Wait for 3 seconds before redirecting
            goto('/home');
        }
    });

    // Helper function to delay the redirect
    async function delay(ms: number) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }
</script>

<div class="font-[sans-serif] max-w-4xl flex items-center mx-auto md:h-screen p-4">
    <div class="grid md:grid-cols-3 items-center shadow-[0_2px_10px_-3px_rgba(6,81,237,0.3)] rounded-xl overflow-hidden">
        <div class="max-md:order-1 flex flex-col justify-center space-y-16 max-md:mt-16 min-h-full bg-gradient-to-r from-gray-900 to-gray-700 lg:px-8 px-4 py-4">
            <div>
                <h4 class="text-white text-lg font-semibold">Create Your Account</h4>
                <p class="text-[13px] text-gray-300 mt-3 leading-relaxed">
                    Welcome to our registration page! Get started by creating your account.
                </p>
            </div>
            <div>
                <h4 class="text-white text-lg font-semibold">Simple & Secure Registration</h4>
                <p class="text-[13px] text-gray-300 mt-3 leading-relaxed">
                    Our registration process is designed to be straightforward and secure. We prioritize your privacy and data security.
                </p>
            </div>
        </div>

        {#if form?.success}
            <div class="md:col-span-2 w-full h-full py-6 px-6 sm:px-16 bg-white items-center justify-center flex">
                <aside class="alert variant-ghost-success">
                    <div class="alert-message">
                        <p>{form?.message} Redirecting... </p>
                    </div>
                </aside>
            </div>
        {:else}
            <form class="md:col-span-2 w-full py-6 px-6 sm:px-16 bg-white" method="post" action="?/SignUp">
                <div class="mb-6">
                    <h3 class="text-gray-800 text-2xl font-bold">Create an account</h3>
                    {#if !form?.success && form?.message !== undefined}
                        <aside class="alert variant-ghost-error m-2">
                            <div class="alert-message">
                                <h6 class="h6">Sign-up Failed</h6>
                                <p>{form?.message}</p>
                            </div>
                        </aside>
                    {/if}
                </div>

                <div class="space-y-6">
                    <div>
                        <label for="username" class="text-gray-800 text-sm mb-2 block">Username</label>
                        <div class="relative flex items-center">
                            <input
                                id="username" 
                                name="username"
                                type="text"
                                required
                                class="text-gray-800 bg-white border border-gray-300 w-full text-sm px-4 py-2.5 rounded-md outline-blue-500"
                                placeholder="Enter username"
                                bind:value={username}
                            />
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label for="first-name" class="text-gray-800 text-sm mb-2 block">First Name</label>
                            <div class="relative flex items-center">
                                <input
                                    id="first-name"
                                    name="first-name"
                                    type="text"
                                    required
                                    class="text-gray-800 bg-white border border-gray-300 w-full text-sm px-4 py-2.5 rounded-md outline-blue-500"
                                    placeholder="Enter first name"
                                    bind:value={firstName}
                                />
                            </div>
                        </div>
                        <div>
                            <label for="last-name" class="text-gray-800 text-sm mb-2 block">Last Name</label>
                            <div class="relative flex items-center">
                                <input
                                    id = "last-name"
                                    name="last-name"
                                    type="text"
                                    required
                                    class="text-gray-800 bg-white border border-gray-300 w-full text-sm px-4 py-2.5 rounded-md outline-blue-500"
                                    placeholder="Enter last name"
                                    bind:value={lastName}
                                />
                            </div>
                        </div>
                    </div>

                    <div>
                        <label for="password" class="text-gray-800 text-sm mb-2 block">Password</label>
                        <div class="relative flex items-center">
                            <input
                                id="password"
                                name="password"
                                type="password"
                                required
                                class="text-gray-800 bg-white border border-gray-300 w-full text-sm px-4 py-2.5 rounded-md outline-blue-500"
                                placeholder="Enter password"
                                bind:value={password}
                            />
                        </div>
                    </div>

                </div>

                <div class="!mt-12">
                    <button type="submit" class="transition ease-in-out delay-75 w-full py-3 px-4 tracking-wider text-sm rounded-md text-white bg-gray-700 hover:bg-gray-800 hover:scale-105 duration-300 focus:outline-none">
                        Create an account
                    </button>
                </div>
                <p class="text-gray-800 text-sm mt-6 text-center">
                    Already have an account? <a href="/login" class="text-blue-600 font-semibold hover:underline ml-1">Login here</a>
                </p>
            </form>
        {/if}
    </div>
</div>
