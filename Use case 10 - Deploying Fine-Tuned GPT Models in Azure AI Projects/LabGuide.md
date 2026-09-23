# Azure AI Foundry Fine-Tuning — Step-by-Step Hands-On Lab

> **Based on:** Microsoft Learn — *Customize a model with fine-tuning*
>
> **Document supplied for this lab:** Microsoft Learn article/PDF, last updated 09/01/2026.

---

## 1. Lab objective

In this lab, you will learn how to:

- Prepare training and validation data for fine-tuning.
- Understand the JSONL conversational format.
- Create a **Supervised Fine-Tuning (SFT)** job in Microsoft Foundry.
- Understand the important options in the fine-tuning screen.
- Monitor training metrics.
- Understand checkpoints and overfitting.
- Deploy the fine-tuned model.
- Test the model.
- Understand continuous fine-tuning.
- Clean up resources and control costs.

Microsoft explains that fine-tuning can provide higher-quality results than prompt engineering alone, allow training on more examples than fit in a request, reduce prompt tokens, and potentially reduce latency, especially with smaller models.

---

# 2. What is fine-tuning? — Easy explanation

Think of a foundation model as a smart employee.

You give the employee instructions:

> "Answer customer questions politely."

That is **prompt engineering**.

You then show the employee a few examples:

> Customer: How do I reset my password?
>
> Assistant: Open the password reset page...

That is **few-shot prompting**.

With fine-tuning, you give the model many examples of exactly how you want it to behave.

```text
Foundation Model
       |
       | Many good examples
       v
Fine-tuning
       |
       v
Customized Model
```

The Microsoft article explains that Foundry uses **Low-Rank Adaptation (LoRA)** for fine-tuning. In simple terms, this means a smaller subset of important model parameters is adapted rather than changing everything.

---

# 3. Prerequisites

Before starting, you need:

- An Azure subscription.
- A Microsoft Foundry project/resource.
- Appropriate Foundry permissions.
- Training data.
- Validation data.

According to the source article:

- Fine-tuning requires the **Foundry Owner** role.
- Foundry Users may train/fine-tune models.
- Deployment requires the appropriate owner/deployment permission.
- You may need additional permission to view quotas and deploy models.

> **Important:** The exact models and regions available to you depend on the current Foundry service and your project region.

---

# 4. Supported customization methods

Microsoft Foundry can expose different customization methods depending on the model.

| Method | Easy explanation | Typical purpose |
|---|---|---|
| **SFT** — Supervised Fine-Tuning | Teach the model using correct input → output examples | Task specialization and most normal fine-tuning scenarios |
| **DPO** — Direct Preference Optimization | Teach the model which responses people prefer | Improving response quality when preference data is available |
| **RFT** — Reinforcement Fine-Tuning | Use reward signals from model graders | More complex behavior optimization |

### For this lab

We will use:

```text
SFT — Supervised Fine-Tuning
```

The Microsoft article's detailed workflow is based on SFT.

---

# 5. Understand the training data

Your training and validation files must be:

- **JSONL**
- Conversational format used by the Chat Completions API
- UTF-8 encoded
- Include a **Byte Order Mark (BOM)**
- Less than **512 MB per file**

## What is JSONL?

JSONL means:

> One JSON object per line.

Example:

```json
{"messages":[{"role":"system","content":"You are a helpful IT support assistant."},{"role":"user","content":"How do I reset my password?"},{"role":"assistant","content":"Open the password reset page and follow the verification steps."}]}
```

Another example is placed on the next line:

```json
{"messages":[{"role":"system","content":"You are a helpful IT support assistant."},{"role":"user","content":"My VPN is not connecting."},{"role":"assistant","content":"Check your internet connection, restart the VPN client, and try again."}]}
```

Each line represents one training example.

---

# 6. Understand the `messages` structure

A normal training example contains:

```text
messages
   |
   +-- system
   |
   +-- user
   |
   +-- assistant
```

### System

Tells the model how it should behave.

Example:

```text
You are a helpful IT support assistant.
Answer briefly and clearly.
```

### User

The question/input.

Example:

```text
How do I reset my password?
```

### Assistant

The answer you want the model to learn.

Example:

```text
Open the password reset page and follow the verification steps.
```

---

# 7. Create your lab dataset

For this lab, use an IT support scenario.

## Example training examples

```json
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"How do I reset my password?"},{"role":"assistant","content":"Open the password reset page, enter your work email, complete verification, and choose a new password."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"My laptop is connected to Wi-Fi but websites do not open."},{"role":"assistant","content":"First disconnect and reconnect to Wi-Fi. If that does not help, restart the browser and check whether other websites open."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"How do I request software installation?"},{"role":"assistant","content":"Open the company software request portal, select the application, provide the business reason, and submit the request."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"What should I do if my account is locked?"},{"role":"assistant","content":"Wait for the lockout period or use the approved account-unlock process. Contact IT support if you cannot unlock it."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"My VPN is not connecting."},{"role":"assistant","content":"Check your internet connection, restart the VPN client, and try again. If it still fails, contact IT support with the error message."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"How can I check my support ticket?"},{"role":"assistant","content":"Open the support portal and select My Tickets to view the current status and recent updates."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"My email is not syncing on my phone."},{"role":"assistant","content":"Check your internet connection, verify the account is enabled for mobile access, and restart the mail application."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"How do I report a suspicious email?"},{"role":"assistant","content":"Use the Report Phishing or Report Suspicious Email option provided by your organization."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"My computer is running slowly."},{"role":"assistant","content":"Close unused applications and restart the computer. If the issue continues, contact IT support for further diagnosis."}]}
{"messages":[{"role":"system","content":"You are a helpful IT support assistant. Answer briefly and clearly."},{"role":"user","content":"Where can I find company policies?"},{"role":"assistant","content":"Open the company intranet and use the Policies or Knowledge Base section."}]}
```

### Dataset recommendation

The source says:

- A fine-tuning job will not proceed with fewer than **10 training examples**.
- However, 10 examples are generally not enough to noticeably influence the model.
- Microsoft recommends starting with about **50 well-crafted examples**.
- Hundreds or thousands may be useful for larger datasets/use cases.
- Poor-quality examples can make performance worse.

### Key rule

> **Quality is more important than blindly adding data.**

Remove:

- Incorrect answers
- Contradictory answers
- Poorly written examples
- Duplicate examples
- Examples that do not represent your real use case

---

# 8. Training data vs validation data

You normally provide two datasets.

## Training dataset

The model learns from this data.

```text
Training data
      |
      v
Model learns patterns
```

## Validation dataset

The model does not use this as normal training data. It is used to evaluate how well training is progressing.

```text
Training data ---> Learning
Validation data -> Checking
```

### Simple rule

Do not simply copy the training dataset into validation.

Use validation examples that represent the same task but are separate examples.

---

# 9. Multiple-turn conversations

You can put several turns in one JSONL line.

Example:

```json
{"messages":[{"role":"system","content":"You are a helpful support assistant."},{"role":"user","content":"What is the capital of France?"},{"role":"assistant","content":"Paris","weight":0},{"role":"user","content":"Can you be more concise?"},{"role":"assistant","content":"Paris.","weight":1}]}
```

## What does `weight` mean?

The source currently supports:

```text
weight = 0
weight = 1
```

Easy explanation:

| Weight | Meaning |
|---|---|
| `0` | Do not train on this assistant message |
| `1` | Train on this assistant message |

---

# 10. Lab: Open Microsoft Foundry

## Step 1 — Sign in

Open Microsoft Foundry and sign in with your Azure account.

Select your project.

---

# 11. Step 2 — Open Fine-tuning

From your project:

```text
Build
  |
  +-- Fine-tune
```

Open **Fine-tune**.

Then select:

```text
Fine-tune
```

in the upper-right corner.

You should now see the:

```text
Fine-tune a model
```

experience.

---

# 12. Step 3 — Select the base model

The **base model** is the model you want to teach.

Think of it as:

```text
Base model = student
Training examples = lessons
Fine-tuning = training
Fine-tuned model = trained student
```

The available models depend on:

- Foundry project region
- Model availability
- Current Microsoft support
- Quotas
- Selected customization method

The source article lists several supported models, including OpenAI models such as:

- `gpt-4o-mini`
- `gpt-4o`
- `gpt-4.1`
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `o4-mini`

It also lists additional supported models/methods.

> Always use the models currently shown as available in your Foundry project.

---

# 13. Step 4 — Choose customization method

For this lab select:

```text
Supervised Fine-Tuning (SFT)
```

Why?

Because we have:

```text
Question ---> Desired answer
```

For example:

```text
User:
How do I reset my password?

Desired answer:
Open the password reset page...
```

---

# 14. Step 5 — Choose training type

This is one of the most important options.

Microsoft documents three training tiers.

## Standard

Easy meaning:

> Train in the current Foundry resource's region.

Use this when:

- Data residency matters.
- You need regional guarantees.

```text
Your region
    |
    v
Training
```

---

## Global

Easy meaning:

> Microsoft can use capacity outside your current region.

Advantages described by the source:

- More affordable than Standard.
- Can use capacity beyond your current region.
- Can provide faster queue times.

Important:

> Data and model weights are copied to the region where training occurs.

Use this only when data residency is not a restriction.

---

## Developer

Easy meaning:

> Use spare/idle capacity to make experimentation cheaper.

Important limitations:

- No latency guarantees.
- No SLA guarantees.
- Jobs can be preempted and resumed.
- No data-residency guarantees.

Good for:

```text
Learning
Testing
Experimentation
```

---

# 15. Training tier — quick comparison

| Training type | Simple meaning | Best fit |
|---|---|---|
| **Standard** | Current region | Data residency requirements |
| **Global** | Capacity beyond current region | Lower cost / queue considerations when residency is not a restriction |
| **Developer** | Idle capacity | Experiments and price-sensitive workloads |

---

# 16. Step 6 — Select training data

You have two choices.

### Existing dataset

Use a dataset already stored in your Foundry project.

### Upload new dataset

Upload your prepared JSONL file.

For this first lab:

```text
Data source
    |
    +-- Upload new dataset
```

Upload your training JSONL.

Foundry automatically validates things such as:

- JSONL format
- UTF-8 with BOM
- File size

---

# 17. Step 7 — Select validation data

Upload/select your validation JSONL.

Remember:

```text
Training data = model learns
Validation data = model is checked
```

Keep the validation examples separate from the training examples.

---

# 18. Step 8 — Suffix

You may see a field called:

```text
Suffix
```

### What is a suffix?

It is a small label that helps you identify your fine-tuned model.

Example:

```text
itsupport-v1
```

Then later:

```text
itsupport-v2
itsupport-v3
```

This makes experiments easier to distinguish.

The source says the suffix can contain up to **18 characters**.

---

# 19. Step 9 — Seed

You may see:

```text
Seed
```

### Easy meaning

A seed helps make training more reproducible.

Think of it like:

```text
Seed = experiment number
```

If you use the same seed and the same job parameters, the source says the results should normally be the same, although rare differences can occur.

### Recommendation

When comparing experiments:

```text
Seed = 12345
```

Keep it the same.

---

# 20. Step 10 — Hyperparameters

This is usually the most confusing part for beginners.

The main parameters are:

```text
batch_size
learning_rate_multiplier
n_epochs
```

Let's understand them one by one.

---

# 21. `batch_size`

### Simple meaning

How many examples the model processes together before updating its parameters.

Imagine you have:

```text
100 training examples
```

If:

```text
batch_size = 10
```

the model processes groups of approximately:

```text
10 examples
10 examples
10 examples
...
```

### Microsoft guidance

The source says:

- Larger batch sizes tend to work better for larger datasets.
- Larger batch sizes mean model parameters are updated less frequently but with lower variance.
- Default and maximum values depend on the base model.
- `-1` calculates the batch size as 0.2% of the training examples.
- Maximum is 256.

### Beginner recommendation

```text
Use the default.
```

Do not change it unless you have a reason.

---

# 22. `learning_rate_multiplier`

### Simple meaning

How strongly the model changes during fine-tuning.

Imagine:

```text
Small learning rate
       |
       v
Small changes
```

versus:

```text
Large learning rate
       |
       v
Large changes
```

The source defines the fine-tuning learning rate as:

```text
Original pre-training learning rate
              ×
Learning-rate multiplier
```

Microsoft recommends experimenting in approximately:

```text
0.02 → 0.2
```

A smaller learning rate can help avoid overfitting.

### Beginner recommendation

Start with the default.

Only experiment after you understand your baseline results.

---

# 23. `n_epochs`

### Simple meaning

How many times the model sees the complete training dataset.

Example:

```text
Dataset
100 examples
```

If:

```text
n_epochs = 1
```

the model sees the dataset once.

If:

```text
n_epochs = 3
```

the model sees it three times.

```text
Epoch 1 -> Dataset
Epoch 2 -> Dataset
Epoch 3 -> Dataset
```

The source says:

```text
n_epochs = -1
```

allows the number of epochs to be determined dynamically.

### Beginner recommendation

Start with the default/dynamic setting.

More epochs are not automatically better.

---

# 24. Hyperparameter cheat sheet

| Parameter | Easy meaning | Beginner choice |
|---|---|---|
| `batch_size` | How many examples are processed together | Default |
| `learning_rate_multiplier` | How strongly the model changes | Default initially |
| `n_epochs` | How many times the dataset is processed | Default / `-1` |

---

# 25. Step 11 — Automatic deployment

You may see:

```text
Automatic deployment
```

### What does this mean?

Normally:

```text
Fine-tune
   |
   v
Model created
   |
   v
You deploy it
```

With automatic deployment:

```text
Fine-tune
   |
   v
Successful training
   |
   v
Automatic deployment
```

This can save time.

According to the source:

- Automatic deployment is supported only for OpenAI models.
- Appropriate deployment permissions are required.

For a learning lab, you can enable it if you want to practice deployment automatically.

---

# 26. Step 12 — Submit the job

Before selecting **Submit**, review:

```text
Base model
Customization method
Training type
Training dataset
Validation dataset
Suffix
Seed
Batch size
Learning rate
Epochs
Automatic deployment
```

Then:

```text
Submit
```

---

# 27. What happens after Submit?

Your job can enter a queue.

Training may take:

```text
Minutes → Hours
```

depending on:

- Model
- Dataset size
- System capacity
- Training configuration

Do not assume that a queued job is broken.

---

# 28. Monitor the training job

Open the job details.

Look for:

```text
Monitor
```

You will see metrics such as:

- `train_loss`
- `full_valid_loss`
- `train_mean_token_accuracy`
- `full_valid_mean_token_accuracy`

---

# 29. `train_loss`

### Easy meaning

How much error the model is making on training data.

Generally:

```text
Lower = better
```

Example:

```text
1.5
1.2
0.9
0.7
```

This indicates training loss is decreasing.

---

# 30. `full_valid_loss`

This is the validation loss.

It tells you how the model performs on the validation dataset.

Generally:

```text
Lower = better
```

You want validation loss to improve as training progresses.

---

# 31. `train_mean_token_accuracy`

### Easy meaning

How many tokens the model predicted correctly in the training batch.

For example:

```text
6 tokens total
5 predicted correctly
```

Accuracy:

```text
5 / 6 = 0.83
```

The source gives essentially this example.

Generally:

```text
Higher = better
```

---

# 32. `full_valid_mean_token_accuracy`

This is token accuracy calculated on validation data at the end of each epoch.

Generally:

```text
Higher = better
```

---

# 33. What should good training look like?

A simple mental model:

```text
Training progresses
       |
       +--> Loss generally goes DOWN
       |
       +--> Accuracy generally goes UP
```

You want both training and validation behavior to remain healthy.

---

# 34. Understanding overfitting

Overfitting means the model becomes too focused on the training examples and does not generalize as well.

Think:

```text
Training data
     |
     v
Model memorizes examples
     |
     X
New questions perform poorly
```

The source says that if training and validation results diverge, you may be overfitting.

Try:

```text
Fewer epochs
        OR
Smaller learning-rate multiplier
```

---

# 35. Checkpoints

At the end of each training epoch, a checkpoint is generated.

Think of a checkpoint as:

> A saved version of the model at that point in training.

```text
Epoch 1 ---> Checkpoint 1
Epoch 2 ---> Checkpoint 2
Epoch 3 ---> Checkpoint 3
```

The source says checkpoints can be:

- Viewed in the Checkpoints area.
- Deployed.
- Used as the target model for subsequent fine-tuning.
- Useful as snapshots before overfitting.

When a job finishes, the three most recent versions are available to deploy.

---

# 36. Step 13 — Deploy the fine-tuned model

After training completes:

1. Open the job details.
2. Review the metrics.
3. Select **Deploy**.
4. Configure deployment settings.
5. Complete deployment.
6. Wait for the deployment to become available.

Deployment requires the appropriate deployment permission.

---

# 37. Step 14 — Test the model

Once deployed, open the Foundry playground.

Test questions that were **not** in the training data.

For example:

```text
I changed my phone. How can I update my MFA method?
```

```text
I cannot open the support portal from home. What should I check first?
```

```text
My VPN connects but internal applications still fail.
```

Observe:

- Does it follow the desired style?
- Is it concise?
- Does it follow your task pattern?
- Does it generalize to questions not seen during training?

---

# 38. Very important: System message

For chat models, the source gives an important warning:

> The system message used for the fine-tuned model should be the same as the system message used during training.

For example, if training used:

```text
You are a helpful IT support assistant. Answer briefly and clearly.
```

use that same system message when testing.

Do not suddenly change it to something completely different.

---

# 39. Compare base model vs fine-tuned model

A good lab exercise is to ask both models the same questions.

| Test | Base model | Fine-tuned model |
|---|---|---|
| Password question | Record answer | Record answer |
| VPN question | Record answer | Record answer |
| Email question | Record answer | Record answer |
| New/unseen question | Record answer | Record answer |

Focus on **observable differences**, not just whether one response sounds nicer.

---

# 40. Continuous fine-tuning

After version 1 is working, you may want to improve it.

The process becomes:

```text
Fine-tuned Model v1
        |
        | New high-quality examples
        v
Fine-tuning
        |
        v
Fine-tuned Model v2
```

The source calls this **continuous fine-tuning**.

For supported OpenAI models, you can select an already fine-tuned model as the starting model and fine-tune it again.

---

# 41. Cleanup

When your lab is finished, clean up.

Delete:

1. Fine-tuned model deployment.
2. Fine-tuned model if no longer needed.
3. Training files if no longer needed.
4. Validation files if no longer needed.

### Important

You cannot delete a fine-tuned model if it still has an existing deployment.

Delete the deployment first.

---

# 42. Cost warning

According to the source:

- A deployed customized model incurs an hourly hosting cost.
- This applies even when there are no chat completion or response API calls.
- An inactive customized-model deployment can be automatically deleted after more than 15 continuous days of inactivity.
- This automatic deletion does **not** delete the underlying customized model.

Therefore:

```text
Lab finished?
      |
      v
Delete unused deployment
```

---

# 43. Troubleshooting

## Problem: Fine-tuning option is missing

Check:

- Project region
- Model availability
- Quota
- Permissions
- Supported customization method

---

## Problem: Dataset upload fails

Check:

```text
JSONL?
UTF-8?
BOM?
< 512 MB?
```

---

## Problem: Job does not start

Check:

- At least 10 training examples.
- Model is supported.
- Selected method is supported.
- Training data is valid.

Remember: 10 is the minimum, not a recommended production dataset size.

---

## Problem: Model quality is poor

First investigate your data.

Check:

- Are answers correct?
- Are examples representative?
- Are examples consistent?
- Are there enough examples?
- Are there contradictory examples?

Do not immediately increase epochs.

---

## Problem: Training looks good but validation gets worse

Possible overfitting.

Try:

```text
Fewer epochs
```

or:

```text
Smaller learning-rate multiplier
```

---

## Problem: Deployment fails

Check that you have the required deployment permission, including the appropriate Foundry Owner/deployment action.

---

## Problem: Fine-tuned chat model behaves unexpectedly

Check the system message.

Make sure it matches the system message used during training.

---

# 44. Recommended first-lab configuration

For a learning lab:

| Setting | Suggested choice |
|---|---|
| Customization method | SFT |
| Base model | A supported model available in your project |
| Training type | Developer for experimentation if its limitations are acceptable; otherwise Standard |
| Training examples | Start around 50 high-quality examples |
| Validation examples | Separate representative examples |
| Suffix | `itsupport-v1` |
| Seed | Fixed value when comparing experiments |
| Batch size | Default |
| Learning-rate multiplier | Default initially |
| Epochs | Default / dynamic |
| Automatic deployment | Optional |

These are **lab-oriented starting choices**, not universal production settings.

---

# 45. Final lab checklist

Use this before finishing the lab.

- [ ] Azure subscription available
- [ ] Microsoft Foundry project created
- [ ] Required permissions available
- [ ] Supported model selected
- [ ] SFT selected
- [ ] Training JSONL prepared
- [ ] Validation JSONL prepared
- [ ] JSONL uses conversational format
- [ ] Files are UTF-8 with BOM
- [ ] Files are below 512 MB
- [ ] At least 10 training examples
- [ ] Preferably about 50+ high-quality training examples
- [ ] Training type understood
- [ ] Suffix configured
- [ ] Seed understood
- [ ] Batch size understood
- [ ] Learning-rate multiplier understood
- [ ] Epochs understood
- [ ] Fine-tuning job submitted
- [ ] Training metrics reviewed
- [ ] Validation metrics reviewed
- [ ] Overfitting checked
- [ ] Checkpoint understood
- [ ] Model deployed if required
- [ ] Fine-tuned model tested
- [ ] Base vs fine-tuned behavior compared
- [ ] Deployment deleted when lab finished
- [ ] Fine-tuned model deleted when no longer required

---

# 46. One-page cheat sheet

| Topic | Remember this |
|---|---|
| Fine-tuning | Teach a model using many examples |
| SFT | Input → desired output examples |
| DPO | Preference-based training |
| RFT | Reward-based training |
| JSONL | One JSON object per line |
| Training data | Used to teach the model |
| Validation data | Used to check training |
| Minimum training examples | 10 |
| Practical starting point | ~50 high-quality examples |
| File size | < 512 MB per file |
| Encoding | UTF-8 with BOM |
| Standard | Regional training/data residency |
| Global | More affordable; training capacity can be outside current region |
| Developer | Lower-cost experimentation; fewer guarantees |
| Batch size | Examples processed together |
| Learning rate | Strength of model updates |
| Epoch | One complete pass through training data |
| Loss | Generally want it to decrease |
| Token accuracy | Generally want it to increase |
| Overfitting | Training improves while validation diverges |
| Checkpoint | Saved model version during training |
| Deployment | Makes model available for inference |
| System message | Keep it consistent with training for chat models |
| Cleanup | Delete unused deployments/models |
| Hosting cost | Deployed customized models have hourly hosting cost |

---

# 47. Lab architecture

```text
                 +----------------------+
                 |  Microsoft Foundry   |
                 |       Project        |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |    Base Model        |
                 |   e.g. supported     |
                 |    OpenAI model      |
                 +----------+-----------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
      +---------------+           +---------------+
      | Training JSONL|           |Validation JSONL|
      +-------+-------+           +-------+-------+
              |                           |
              +-------------+-------------+
                            |
                            v
                 +----------------------+
                 | Fine-tuning Job      |
                 | SFT + Hyperparameters|
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Metrics / Checkpoints|
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Fine-tuned Model     |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Deployment           |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Playground / API     |
                 +----------------------+
```

---

# 48. Key takeaways

### Remember these 10 things

1. **Fine-tuning is learning from examples.**
2. **SFT is the easiest starting point for normal task specialization.**
3. **Good data is more important than simply having lots of data.**
4. **10 examples is only the minimum; Microsoft recommends starting around 50 well-crafted examples.**
5. **Training and validation data serve different purposes.**
6. **Start hyperparameters with sensible defaults.**
7. **Watch loss and token accuracy during training.**
8. **If validation diverges, investigate overfitting.**
9. **A checkpoint is a saved version of the model during training.**
10. **Delete unused deployments to avoid unnecessary hosting costs.**

---

## Source and Microsoft Learn reference

This lab is based on the supplied Microsoft Learn article:

**Customize a model with fine-tuning**

### Official Microsoft Learn article

https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning?tabs=oai-sdk%2Cpython&pivots=programming-language-studio

**Official reference:** [Microsoft Learn — Customize a model with fine-tuning](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/fine-tuning?tabs=oai-sdk%2Cpython&pivots=programming-language-studio)

The supplied document states that the article covers dataset preparation, fine-tuning job creation, monitoring, deployment, evaluation, continuous fine-tuning, and cleanup.

**Important:** Microsoft Foundry model availability, regions, quotas, permissions, pricing, and portal screens can change. For a live lab, verify the current options shown in your Foundry project.
