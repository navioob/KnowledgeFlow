<script lang="ts">
	import type {ActionData } from './$types';
	import { onMount } from 'svelte';
	import lottie from 'lottie-web';
	import animationData from '$lib/components/animations/walking-girl.json';
	import { goto } from '$app/navigation';

	/** @type {import('./$types').ActionData} */
	export let form: ActionData;

	let animationContainer: HTMLElement;

	onMount(async () => {
		lottie.loadAnimation({
			container: animationContainer,
			animationData,
			loop: true,
			autoplay: true
		});

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

<div class="font-[sans-serif]">
	<div class="min-h-screen flex fle-col items-center justify-center py-6 px-4">
		<div class="grid md:grid-cols-2 items-center gap-4 max-w-6xl w-full">
			<div class="flex col-span-2 justify-center items-start py-10">
				<h1 class="h1">Welcome to KnowledgeFlow</h1>
			</div>
			<div
				class="card bg-white border border-gray-300 rounded-lg p-6 max-w-md shadow-[0_2px_22px_-4px_rgba(93,96,127,0.2)] max-md:mx-auto"
			>
				{#if form?.success}
					<div
						class="md:col-span-2 w-full h-full py-6 px-6 sm:px-16 bg-white items-center justify-center flex"
					>
						<aside class="alert variant-ghost-success">
							<div class="alert-message">
								<p>{form?.message} Redirecting...</p>
							</div>
						</aside>
					</div>
				{:else}
					<form class="space-y-4" method="post" action="?/Login">
						<div class="mb-8">
							<h3 class="text-gray-800 text-3xl font-extrabold">Sign in</h3>
							<p class="text-gray-500 text-sm mt-4 leading-relaxed">
								Sign in to your account and explore a world of possibilities. Your journey begins
								here.
							</p>
							{#if !form?.success && form?.message!== undefined}
								<aside class="alert variant-ghost-error m-2">
									<div class="alert-message">
										<h6 class="h6">Login Unsuccesful</h6>
										<p>{form?.message}</p>
									</div>
								</aside>
							{/if}
						</div>
						<div>
							<label for="username" class="text-gray-800 text-sm mb-2 block">Username</label>
							<div class="relative flex items-center">
								<input
									id="username"
									name="username"
									type="text"
									required
									class="input bg-white focus:outline-none focus:ring focus:border-blue-500"
									placeholder="Enter username"
								/>
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
									class="input bg-white focus:outline-none focus:ring focus:border-blue-500"
									placeholder="Enter password"
								/>
							</div>
						</div>
						<div class="!mt-8">
							<button
								class="transition ease-in-out delay-75 w-full shadow-xl py-3 px-4 text-sm tracking-wide rounded-lg text-white bg-gray-600 hover:bg-gray-700 hover:scale-105 duration-300 focus:outline-none"
							>
								Log in
							</button>
						</div>

						<p class="text-sm !mt-8 text-center text-gray-800">
							Don't have an account? <a
								href="/signup"
								class="text-blue-600 font-semibold hover:underline ml-1 whitespace-nowrap"
								>Register here</a
							>
						</p>
					</form>
				{/if}
			</div>
			<div class="lg:h-[400px] md:h-[300px] max-md:mt-8" bind:this={animationContainer}></div>
		</div>
	</div>
</div>
