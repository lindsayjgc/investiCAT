import { openai } from '@ai-sdk/openai';
import { Agent } from '@mastra/core/agent';
import { ALL_TOOLS, TOOL_REGISTRY } from '../tools/toolDefinitions';
import { generateCategorizedToolDescriptions } from '@cedar-os/backend';
import { memory } from '../memory';

/**
 * Example starter agent for Cedar-OS + Mastra applications
 *
 * This agent serves as a basic template that you can customize
 * for your specific use case. Update the instructions below to
 * define your agent's behavior and capabilities.
 */
export const starterAgent = new Agent({
  name: 'Starter Agent',
  instructions: ` 
<role>
You are given a document of information and possibly an occurrence. </role>

<primary_function>
You will extract the following data from a document: the EVENT that occurred, the DATE or WHEN that event occurred, the LOCATION of that occurrence, and any ENTITY that participated in the event. 
Please structure this nicely. 
We plan to organize this data as a knowledge graph. 
- \"Event\" OCCURRED_ON \"Date\"
- \"Event\" OCCURRED_AT \"Location\"
- \"Entity\" PARTICIPATES_IN \"EVENT\"
- And the input \"Document\" MENTIONS \"Entity\" and \"Document\" MENTIONS \"Event\".
</primary_function>

<tools_available>
You have access to:
${generateCategorizedToolDescriptions(
  TOOL_REGISTRY,
  Object.keys(TOOL_REGISTRY).reduce(
    (acc, key) => {
      acc[key] = key;
      return acc;
    },
    {} as Record<string, string>,
  ),
)}
</tools_available>

<response_guidelines>
When responding:
- Be helpful, accurate, and concise
- Use your tools to make UI changes when users request them
- Explain what changes you're making to the interface
- Format your responses in a clear, readable way
</response_guidelines>

  `,
  model: openai('gpt-4o-mini'),
  tools: Object.fromEntries(ALL_TOOLS.map((tool) => [tool.id, tool])),
  memory,
});
