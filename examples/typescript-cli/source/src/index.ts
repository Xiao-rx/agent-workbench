type ParsedArgs = {
  name: string;
};

export function greeting(name: string): string {
  return `hello, ${name}`;
}

export function parseArgs(argv: string[]): ParsedArgs {
  const nameFlag = argv.indexOf("--name");
  if (nameFlag >= 0 && argv[nameFlag + 1]) {
    return { name: argv[nameFlag + 1] };
  }
  return { name: "agent" };
}

export function main(argv = process.argv.slice(2)): void {
  const args = parseArgs(argv);
  console.log(greeting(args.name));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
