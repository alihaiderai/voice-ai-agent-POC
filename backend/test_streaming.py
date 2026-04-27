"""
Test script for real-time voice + text streaming with GPT-4o
"""
import asyncio
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def test_text_streaming():
    """Test GPT-4o text streaming"""
    print("=" * 50)
    print("TEST 1: Text Streaming (GPT-4o)")
    print("=" * 50)
    
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Tell me a short story about AI"}],
        stream=True
    )
    
    print("\nStreaming text (word by word):\n")
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end='', flush=True)
    
    print("\n\n✅ Text streaming works!\n")


async def test_tts_streaming():
    """Test OpenAI TTS streaming"""
    print("=" * 50)
    print("TEST 2: TTS Streaming")
    print("=" * 50)
    
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input="Hello! This is a test of real-time text to speech streaming.",
        response_format="mp3"
    )
    
    # Save to file
    with open("test_streaming_audio.mp3", "wb") as f:
        async for chunk in response.iter_bytes():
            f.write(chunk)
            print(".", end='', flush=True)
    
    print("\n\n✅ TTS streaming works! Audio saved to test_streaming_audio.mp3\n")


async def test_combined_streaming():
    """Test combined text + TTS streaming (real-time)"""
    print("=" * 50)
    print("TEST 3: Combined Real-time Streaming")
    print("=" * 50)
    
    # Step 1: Stream text from GPT-4o
    print("\n📝 Generating text...\n")
    
    text_stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Say hello in a friendly way"}],
        stream=True
    )
    
    full_text = ""
    async for chunk in text_stream:
        if chunk.choices[0].delta.content:
            text_chunk = chunk.choices[0].delta.content
            full_text += text_chunk
            print(text_chunk, end='', flush=True)
    
    print("\n\n🔊 Converting to speech...\n")
    
    # Step 2: Convert to speech
    audio_response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=full_text,
        response_format="mp3"
    )
    
    with open("test_combined_audio.mp3", "wb") as f:
        async for chunk in audio_response.iter_bytes():
            f.write(chunk)
    
    print("✅ Combined streaming works!")
    print(f"📄 Text: {full_text}")
    print("🔊 Audio saved to test_combined_audio.mp3\n")


async def test_realtime_word_by_word():
    """Test true real-time: generate text word-by-word and convert to audio chunks"""
    print("=" * 50)
    print("TEST 4: Real-time Word-by-Word Streaming")
    print("=" * 50)
    print("\nThis simulates how Retell.ai works:\n")
    
    # Stream text
    text_stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Count from 1 to 5 slowly"}],
        stream=True
    )
    
    sentence_buffer = ""
    
    async for chunk in text_stream:
        if chunk.choices[0].delta.content:
            text_chunk = chunk.choices[0].delta.content
            sentence_buffer += text_chunk
            print(text_chunk, end='', flush=True)
            
            # When we have a complete sentence, convert to audio
            if any(punct in text_chunk for punct in ['.', '!', '?', '\n']):
                if sentence_buffer.strip():
                    print(f" [🔊 Playing audio...]", end='', flush=True)
                    
                    # Convert this sentence to audio
                    audio_response = await client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=sentence_buffer.strip(),
                        response_format="mp3"
                    )
                    
                    # In real app, we'd play this audio immediately
                    # For test, we just indicate it's ready
                    print(" ✅")
                    
                    sentence_buffer = ""
    
    print("\n\n✅ Real-time word-by-word streaming works!")
    print("This is how we'll implement it in production.\n")


async def main():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("REAL-TIME STREAMING TESTS")
    print("Testing GPT-4o + OpenAI TTS")
    print("=" * 50 + "\n")
    
    try:
        # Test 1: Text streaming
        await test_text_streaming()
        await asyncio.sleep(1)
        
        # Test 2: TTS streaming
        await test_tts_streaming()
        await asyncio.sleep(1)
        
        # Test 3: Combined
        await test_combined_streaming()
        await asyncio.sleep(1)
        
        # Test 4: Real-time word-by-word
        await test_realtime_word_by_word()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! ✅")
        print("=" * 50)
        print("\nConclusion:")
        print("✅ GPT-4o supports text streaming")
        print("✅ OpenAI TTS supports audio streaming")
        print("✅ We can combine them for real-time experience")
        print("\nNext step: Integrate into main app\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. OPENAI_API_KEY is set in .env")
        print("2. You have access to GPT-4o model")
        print("3. Internet connection is working\n")


if __name__ == "__main__":
    asyncio.run(main())
