<!-- YOU CAN DELETE EVERYTHING IN THIS PAGE -->
<script lang="ts">
	import { onMount } from 'svelte';
	// Components
	import lottie from 'lottie-web';
	import animationData from '$lib/components/animations/document-upload.json';
	import chatAnimationData from '$lib/components/animations/girl-sitting-chat.json';
	import { Avatar, CodeBlock, FileDropzone, ProgressBar, getToastStore, type ToastSettings, ListBox, ListBoxItem, ProgressRadial, Accordion, AccordionItem } from '@skeletonlabs/skeleton';
	import '@fortawesome/fontawesome-free/css/all.min.css'
	//setup toast messages

	const toastStore = getToastStore();
	const startDocumentUpload: ToastSettings = {
		message: 'Uploading paper started.',
		timeout: 5000, //5secs,
		background: "variant-filled-tertiary"
	};

	const finishDocumentUpload: ToastSettings = {
		message: 'Paper upload completed!',
		timeout: 5000, //5secs,
		background: "variant-filled-success"
	};

	// Types
	interface MessageFeed {
		id: number;
		bot: boolean;
		avatar: number;
		name: string;
		timestamp: string;
		message: string;
		reference: [];
		color: string;
	}

	// States
	// Get session id as user id stored in locale
	export let data;
    let user = data.user;
	let documentList = data.documentList;
	let documentUploading = false;
	let generatingAnswer = false;
	let selectedDocuments: string[] = []
	let elemChat: HTMLElement;
	let currentMessage = '';
	const user_id = user.id
	let files:FileList; // Stores dropped files (bind)
	// let currentDocumentId: string = documentList[0].document_id;
	const document_limit = 5;
	let animationContainer: HTMLElement;
	let animationContainer2: HTMLElement;
	// delete document triggers for each buttons
	let deleteDocumentTrigger = {};

	// Reactive statements - should be at the top level of the script
	$: if (documentList && documentList.length > 0) {
		documentList.forEach(dict => {
			if (!deleteDocumentTrigger[dict.document_id]) {
				deleteDocumentTrigger[dict.document_id] = false;
			}
		});
	}

	const lorem = "Test"

	// List of Documents

	function sleep(ms: number) {
		return new Promise(resolve => setTimeout(resolve, ms));
	}

	// Messages (with histories)
	let messageFeed: MessageFeed[] = [];

	// Function to fetch documents
    async function fetchDocuments() {
		const requestOptions = {
                method: "GET",
                redirect: "follow"
              };
              
		const url = (
			'http://127.0.0.1:8000/document/list?' +
			new URLSearchParams({ user_id: user_id}).toString()
		);

        try {
            const res = await fetch(url, requestOptions);
            if (!res.ok) throw new Error('Failed to fetch documents');
            let response = await res.json();

			//set document delete trigger
			response.content.forEach(dict => {
				deleteDocumentTrigger[dict.document_id] = false;
			});

			console.log(deleteDocumentTrigger)

        	return response.content;
        } catch (error) {
            console.error('Error fetching documents:', error);
        }
    }

	// Function to DELETE documents
    async function deleteDocument(document_id: string) {
		// Make a local update first for immediate UI feedback
		deleteDocumentTrigger = { ...deleteDocumentTrigger, [document_id]: true };

		console.log("Selected Documents after deleting", selectedDocuments)

		const requestOptions = {
                method: "DELETE",
                redirect: "follow"
              };
              
		const url = (
			'http://127.0.0.1:8000/document/delete?' +
			new URLSearchParams({ user_id: user_id, document_id: document_id}).toString()
		);

        try {
            const res = await fetch(url, requestOptions);
            if (!res.ok) throw new Error('Failed to delete document');

			//remove being selected
			// Remove the document from selectedDocuments array
			selectedDocuments = selectedDocuments.filter(id => id !== document_id);
			
			// Create a new object to trigger reactivity
			const newDeleteDocumentTrigger = { ...deleteDocumentTrigger };
			delete newDeleteDocumentTrigger[document_id];
			deleteDocumentTrigger = newDeleteDocumentTrigger;
			
			// Update document list
            const newDocuments = await fetchDocuments();
			documentList = [...newDocuments]; 
			console.log("Updated Document", documentList)

        } catch (error) {
            console.error('Error deleting document:', error);
            // Reset the trigger if there's an error
            deleteDocumentTrigger = { ...deleteDocumentTrigger, [document_id]: false };
        }
    }

	// FUNCTIONS Upload Files
	async function uploadFile() {
		// Important: Trigger reactivity by creating a new state
		documentUploading = true;
        
        // Show toast at the start
        toastStore.trigger(startDocumentUpload);

        if (!files || files.length === 0) {
            console.error("No file selected.");
            documentUploading = false;
            return;
        }

        const file = files[0]; // Assuming single file upload
        const formData = new FormData();
        formData.append("file", file, file.name);
        formData.append("user_id", user_id); // Change user_id as needed

        const requestOptions = {
            method: "POST",
            body: formData,
            redirect: "follow"
        };

        try {
            const response = await fetch("http://127.0.0.1:8000/document/upload", requestOptions);
            const result = await response.text();
            console.log("Upload successful:", result);
            
            // Show completion toast
            toastStore.trigger(finishDocumentUpload);
            
            // Update state to trigger reactivity
            documentUploading = false;
            
            // Fetch updated documents
            await sleep(1000); // Allow backend time to process
            const newDocuments = await fetchDocuments();
            documentList = [...newDocuments]; 
            console.log("Updated Document", documentList);
        } catch (error) {
            console.error("Upload error:", error);
            documentUploading = false; // Make sure to reset the state on error
        }
    }
	
	// FUNCTIONS Messages
	async function generateAnswer(query:string) {

		const selectedDocumentList = documentList.filter(document => selectedDocuments.includes(document.document_id));

		// Prepare the request body
		const requestBody = {
			query: query,
			user_id: user_id,
			list_summary: selectedDocumentList
		};

		try {
			const response = await fetch('http://127.0.0.1:8000/agent/generate-answer', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(requestBody)
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const res = await response.json();

			// Extract answer and references from the response
			let answer = res.content.answer;
			let references = res.content.references;

			return {answer, references}

		} catch (error) {
			console.error('Error generating answer:', error);
			throw error;
		}


	}

	// For some reason, eslint thinks ScrollBehavior is undefined...
	// eslint-disable-next-line no-undef
	function scrollChatBottom(behavior?: ScrollBehavior): void {
		if (elemChat) {
			elemChat.scrollTo({ top: elemChat.scrollHeight, behavior });
		}
	}

	function getCurrentTime(): string {
		const now = new Date();
		const hours = String(now.getHours()).padStart(2, '0');  // Add leading zero if < 10
		const minutes = String(now.getMinutes()).padStart(2, '0');  // Add leading zero if < 10
		return `${hours}:${minutes}`;
	}


	function getCurrentDate(): string {
    	return new Date().toLocaleDateString('en-MY');
	}

	function startBotThinking(): void {
		const newMessage = {
			bot: true,
			avatar: 48,
			name: 'Bot',
			timestamp: `${getCurrentDate()} @ ${getCurrentTime()}`,
			message: "<think>",
			reference: [],
			color: 'variant-soft-primary'
		};

		messageFeed = [...messageFeed, newMessage];
	}

	function stopBotThinking(): void {
		messageFeed = messageFeed.slice(0, -1);
	}

	async function addBotMessage(answer: any): void {
		const newMessage = {
			bot: true,
			avatar: 48,
			name: 'Bot',
			timestamp: `${getCurrentDate()} @ ${getCurrentTime()}`,
			message: answer.answer,
			reference: answer.references,
			color: 'variant-soft-primary'
		};
		// Update the message feed
		messageFeed = [...messageFeed, newMessage];
		
		// Smooth scroll to bottom
		// Timeout prevents race condition
		setTimeout(() => {
			scrollChatBottom('smooth');
		}, 0);

	}

	async function addUserMessage(): void {
		if (!currentMessage.trim()) return;
		
		generatingAnswer = true;
		const newMessage = {
			bot: false,
			avatar: 12,
			name: 'You',
			timestamp: `${getCurrentDate()} @ ${getCurrentTime()}`,
			message: currentMessage,
			reference: [],
			color: 'variant-soft-primary'
		};
		// Update the message feed
		messageFeed = [...messageFeed, newMessage];
		
		// Store current message before clearing
		const messageToSend = currentMessage;
		
		// Clear prompt immediately for better UX
		currentMessage = '';
		
		// Smooth scroll to bottom
		setTimeout(() => {
			scrollChatBottom('smooth');
		}, 0);

		// Process answer
		try {
			//Start bot thinking process
			startBotThinking();
			const generated_answer = await generateAnswer(messageToSend);
			//Stop bot thinking process
			stopBotThinking();
			await addBotMessage(generated_answer);
		} catch (error) {
			// Handle error, maybe show error message
			console.error("Error generating answer:", error);
			stopBotThinking();
			// Add error message to chat
			messageFeed = [...messageFeed, {
				bot: true,
				avatar: 48,
				name: 'Bot',
				timestamp: `${getCurrentDate()} @ ${getCurrentTime()}`,
				message: "Sorry, I encountered an error processing your request.",
				reference: [],
				color: 'variant-soft-error'
			}];
		} finally {
			generatingAnswer = false;
		}
	}

	function onPromptKeydown(event: KeyboardEvent): void {
		if (['Enter'].includes(event.code) && !event.shiftKey && !generatingAnswer) {
			event.preventDefault();
			addUserMessage();
		}
	}

	// When DOM mounted, initialize animations and state
	onMount(() => {
		// Initialize animations
		if (animationContainer) {
			lottie.loadAnimation({
				container: animationContainer,
				animationData: animationData,
				loop: true,
				autoplay: true
			});
		}
		
		if (animationContainer2) {
			lottie.loadAnimation({
				container: animationContainer2,
				animationData: chatAnimationData,
				loop: true,
				autoplay: true
			});
		}
		
		// Initialize document delete triggers
		if (documentList && documentList.length > 0) {
			documentList.forEach(doc => {
				deleteDocumentTrigger[doc.document_id] = false;
			});
		}
		
		scrollChatBottom();
	});
	
</script>


<div class="chat w-full h-full grid grid-cols-1 lg:grid-cols-[30%_1fr]">
	<!-- Navigation -->
	<div class="hidden lg:grid grid-rows-[auto_1fr_auto] border-r border-surface-500/30">
		<!-- Upload File -->
		<header class="border-b border-surface-500/30 p-4">
			<div class="card m-1 p-2 shadow-lg p-2">
				<small class="opacity-50">Upload your paper</small>
				<!-- Add Loading bar if the paper is uploading -->
				{#if documentUploading}
					<ProgressBar />
				{:else}
					{#if documentList.length === document_limit}
						<FileDropzone name="files" bind:files={files} on:change={uploadFile} disabled>
							<svelte:fragment slot="message">File limit reached!</svelte:fragment>
							<svelte:fragment slot="meta">Please remove some documents before uploading.</svelte:fragment>
						</FileDropzone>
					{:else}
						<FileDropzone name="files" bind:files={files} on:change={uploadFile} disabled={documentUploading}>
							<svelte:fragment slot="meta">Only PDF is allowed.</svelte:fragment>
						</FileDropzone>
					{/if}
				{/if}
			</div>
		</header>
		<!-- List -->
		<div class="p-4 space-y-4 overflow-y-auto">
			<div class="flex flex-col space-y-1">
				{#if documentList.length===0}
				<!-- Adding logic to trigger animation and message if the document list is empty -->
					<div class="grid justify-items-center p-2">
						<h1 class="h2 m-3 p-2">Upload your papers <br> to get started.</h1>
						<div class="lg:h-[200px] md:h-[300px] max-md:mt-8" bind:this={animationContainer}></div>
					</div>
				{:else}
					<div class="card m-1 p-2 shadow-lg">
						<div class="grid grid-cols-2 ">
							<small class="grid opacity-50 p-2 justify-items-start">List of Your Papers</small>
							<div class="grid opacity-50 p-2 justify-items-end">
								{#if documentList.length === document_limit}
									<span class="badge variant-filled-warning">
										{documentList.length}/{document_limit}
									</span>
								{:else}
									<span class="badge variant-ghost-success">
										{documentList.length}/{document_limit}
									</span>
								{/if}
							</div>
						</div>
						<small class="grid opacity-50 p-2 justify-items-center">
							{#if selectedDocuments.length === 0}
								Select a document to start asking!
							{:else}
								- You have selected {selectedDocuments.length} documents for querying -
							{/if}
						</small>
						<ListBox multiple rounded-none>
							{#each documentList as document}
								<ListBoxItem class="border-2 bg-surface-300/500 border-surface-200" bind:group={selectedDocuments} name="medium" value={document.document_id}>
									<svelte:fragment slot="lead">
										<i class="fa-regular fa-file"></i>
									</svelte:fragment>
									{document.document_title}
									<svelte:fragment slot="trail">
										{#if deleteDocumentTrigger[document.document_id]}
											<button type="button" class="btn-icon variant-ghost" disabled>
												<i class="fa-solid fa-rotate fa-spin"></i>
											</button>
										{:else}
											<button type="button" class="btn-icon variant-ghost" on:click={() => deleteDocument(document.document_id)}>
												<i class="fa-solid fa-xmark"></i>
											</button>
										{/if}
									</svelte:fragment>
								</ListBoxItem>
							{/each}
						</ListBox>
					</div>
				{/if}
			</div>
		</div>
	</div>

	
	<!-- Chat -->
	{#if documentList.length===0}
		<div class="grid grid-flow-row grid-row-2 p-2 justify-items-center">
			<h1 class="h2 mt-20 p-2">Get your knowledge flowing.</h1>
			<div class="lg:h-[400px] md:h-[300px] max-md:mt-8" bind:this={animationContainer2}></div>
		</div>
	{:else}
		<div class="h-full grid grid-row-[1fr_auto]">
			
			<!-- Conversation -->
			<section bind:this={elemChat} class="h-[80vh] p-4 overflow-y-auto space-y-4">
				{#each messageFeed as bubble}
					{#if bubble.bot === true}
						<!-- If answer generation is still loading (when bot is thinking) -->
						{#if bubble.message === "<think>"}
							<div class="grid grid-cols-[auto_1fr] gap-2">
								<Avatar src="https://i.pravatar.cc/?img={bubble.avatar}" width="w-12" />
								<div class="card p-4 variant-soft rounded-tl-none space-y-2">
									<header class="flex justify-between items-center">
										<p class="font-bold">{bubble.name}</p>
										<small class="opacity-50">{bubble.timestamp}</small>
									</header>
									<!-- Thinking Message and Loading Spinner -->
									<div class="flex items-center text-gray-700">
										<svg class="mr-2 h-5 w-5 animate-spin text-gray-500" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
										  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
										  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
										</svg>
										Thinking...
									</div>
								</div>
							</div>
						{:else}
						<!-- Bot Replies -->
							<div class="grid grid-cols-[auto_1fr] gap-2">
								<Avatar src="https://i.pravatar.cc/?img={bubble.avatar}" width="w-12" />
								<div class="card p-4 variant-soft rounded-tl-none space-y-2">
									<header class="flex justify-between items-center">
										<p class="font-bold">{bubble.name}</p>
										<small class="opacity-50">{bubble.timestamp}</small>
									</header>
									<p>
										{bubble.message}
										<br><br>
										{#if bubble.reference && bubble.reference.length != 0}
											<Accordion class="border-2 shadow-xs">
												<AccordionItem>
													<svelte:fragment slot="summary">References</svelte:fragment>
													<svelte:fragment slot="content">
														{#each bubble.reference as reference}
															{reference.reference_id}. {reference.title} <br>
														{/each}
													</svelte:fragment>
												</AccordionItem>
											</Accordion>
										{/if}	
									</p>
								</div>
							</div>
						{/if}
					{:else}
						<div class="grid grid-cols-[1fr_auto] gap-2">
							<div class="card p-4 rounded-tr-none space-y-2 {bubble.color}">
								<header class="flex justify-between items-center">
									<p class="font-bold">{bubble.name}</p>
									<small class="opacity-50">{bubble.timestamp}</small>
								</header>
								<p>{bubble.message}</p>
							</div>
							<Avatar src="https://i.pravatar.cc/?img={bubble.avatar}" width="w-12" />
						</div>
					{/if}
				{/each}
			</section>
			<!-- Prompt -->
			<section class="border-t border-surface-500/30 p-4">
				<div class="input-group input-group-divider grid-cols-[1fr_auto] rounded-container-token">
					<textarea
						bind:value={currentMessage}
						class="bg-transparent border-0 ring-0"
						name="prompt"
						id="prompt"
						placeholder="Write a message..."
						rows="1"
						on:keydown={onPromptKeydown}
						disabled={generatingAnswer}
					></textarea>
					<button 
						class={currentMessage ? 'variant-filled-primary' : 'input-group-shim'} 
						on:click={addUserMessage} 
						disabled={generatingAnswer || !currentMessage.trim()}
					>
						<i class="fa-solid fa-paper-plane"></i>
					</button>
				</div>
			</section>
		</div>
	{/if}
</div>