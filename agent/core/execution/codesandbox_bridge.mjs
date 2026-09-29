import { CodeSandbox } from "@codesandbox/sdk";

const input = await readStdin();
const request = JSON.parse(input);

const apiKey = process.env.CSB_API_KEY;

if (!apiKey) {
  throw new Error("CSB_API_KEY is not configured.");
}

const sdk = new CodeSandbox(apiKey);

let sandbox;

if (request.sandbox_id) {
  sandbox = await sdk.sandboxes.get(request.sandbox_id);
} else {
  sandbox = await sdk.sandboxes.create();
}

const client = await sandbox.connect();

try {
  const result = await client.commands.run(request.command, {
    cwd: request.cwd || undefined,
    timeoutMs: Math.max(1, Number(request.timeout || 30)) * 1000,
  });

  const exitCode = result.exitCode ?? null;

  process.stdout.write(
    JSON.stringify({
      success: exitCode === 0,
      stdout: result.stdout ?? "",
      stderr: result.stderr ?? "",
      exit_code: exitCode,
      timed_out: false,
      sandbox_id: sandbox.id,
    }),
  );
} catch (error) {
  const message =
    error instanceof Error ? error.message : String(error);

  process.stdout.write(
    JSON.stringify({
      success: false,
      stdout: "",
      stderr: message,
      exit_code: null,
      timed_out: /timeout|timed out|deadline/i.test(message),
      sandbox_id: sandbox.id,
    }),
  );
}

async function readStdin() {
  let data = "";

  for await (const chunk of process.stdin) {
    data += chunk;
  }

  return data;
}
