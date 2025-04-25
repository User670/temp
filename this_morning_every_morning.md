In this video https://www.youtube.com/watch?v=F4KQ8wBt1Qg , the creator Fractal Philosophy gave an example of a phrase that a language model would have difficulty understanding. The phrase is:

> 今朝毎朝

This is an English-Japanese bilingual pun. While the literal words mean "this morning, every morning", the intended meaning is a phonetic-based pun (reads "kesa maiasa", sounds like "kiss my ass").

The creator concluded that the AI models lacked context to reach the correct conclusion - just asking about the word gives interesting interpretations but nowhere near correct; however asking in a way that provides contexts will more liekly get to the correct conclusion.

One thing I like to do with AI models is to interactively let the AI learn more about what they need to solve a task. I'll prompt the AI to analyse the question, and ask any questions that would help them do the task, then I'll answer the questions for the AI to better handle the task. So I decided to see if this path leads to anything interesting for this bilingual pun.

The AI model I used is Deepseek R1 (chain of thought reasoner). I asked it in Chinese because it seems like that AI works best in Chinese, although it does make it slightly harder to think about English when the context is in Chinese.

I can't fully translate the whole conversation (the chain-of-thought part is especially long), so I'll summarize what I got.

# The summary

**Me:**

I've seen someone use this question to demonstrate the weaknesses in interpreting language. Please try to solve this question.

Every time you respond, please try to answer the question, and then tell me what other information you need from me in order to help you answer it.

The question is this: What does the Japanese "今朝毎朝" mean?

**DeepSeek:**

今朝毎朝 isn't a word per-se. It is composed of two words,
- 今朝 (kesa), meaning "this morning",
- 毎朝 (maiasa), meaning "every morning".

When it's written next to each other like this, it could be a typo, or a special usage or dialect.

Questions:
1. Is there a full sentence or context?
2. What's the source of the phrase (like a conversation, some text, some lyrics of a song)?
3. Could there be a typo (like a missing punctuation or an auxiliary word)?

**Me:**
1. There is no textual context. The phrase appears on its own.
2. Ditto.
3. No typos here. Just these four characters, no punctuation or other characters.

**Deepseek:**

There are these possibilities:
- syntatically,
  - it could be a shortening of "今朝から毎朝" (meaning "every morning, starting from this morning"), but Japanese doesn't have a shortening rule like this
  - it could imply some contrast by placing these words together, but this requires additional grammatical structure
- phonetically,
  - it could be a pun, like reading "koncho maicho" might sound like Japanese for "this trillion, every trillion", but the reading is uncommon.
  - it could be forced compression to fit the syllable count restriction in poetry.
- visually,
  - it could be a riddle based on the shape of the characters, but such riddles isn't a tradition in Japan. *(translator's note: althouth they definitely are a thing in China)*

Current conclusion:

This word is **very likely a made-up expression**, with purpose likely being
- to test LLM's ability to deduce nonstandard combinations
- to imitate common mistakes by Japanese learners (eg omitting the particle "kara")
- as a riddle or pun (more info needed)

Questions:
1. Does it involve specific pronunciation (like a nonstandard reading or a dialect)?
2. Does it relate to pop culture (like an in-universe term in an anime or a game)?
3. Is it a mistake by a Chinese native speaker (does the phrase mean anything in CHinese)?

**Me:**
1. Yes, it's related to pronunciation. Please try to poke around for how exactly this goes, and you can ask if you need to.
2. Nothing to do with pop culture.
3. Not from a Chinese native speaker. This comes from an English native speaker, and it's not a mistake, they intentionally wrote that.

**Deepseek:**

*(It mainly considered on-yomi of the characters, although nothing that makes sense came out of this train of thought. It also considered it's probably just trying to semantically put them together and it was wrong.)*

Final key points to confirm:
1. Is it clearly meant to be read in on-yomi (like "kin chou mai chou") as opposed to kun-yomi (kesa maiasa)?
2. Is it related to abbreviation of the romaji (like "KMYM")?
3. Is it related to an English pun (like "kinchou mychou" sounding like some English phrase)?

(If we cannot get further confirmation, then this word should be analysed as an experimental coined word with no actual meaning.)

**Me:**
1. It's read "kesa maiasa".
2. Nothing to do with abbreviation.
3. It's a pun.

**Deepseek:**

Analysing the pronunciation gives "case a / kiss a" + "my ass a". Could be "kiss my ass", and hiding the profanity behind the serious kanji representation for a humorous effect.

Final confirmation:
1. Do you accept this phrase as an English profanity pun ("Kiss my ass", disguised as Japanese)?
2. Could it be pun on a different English phrase (like "case my...")?

**Me:**

Correct. This is a Japanese-English bilingual pun on "kiss my ass".

**Deepseek:**

*(It goes on an analysis of the pun itself, and then tried to analyse why AI models have issue with this question. However, the back end retracted this message and replaced with a "I can't answer that" error message.)*

