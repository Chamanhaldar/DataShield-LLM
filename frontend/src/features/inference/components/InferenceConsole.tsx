import { useEffect, useMemo, useState, type ChangeEvent } from "react";
import {
  Alert,
  AlertDescription,
  AlertIcon,
  Box,
  Button,
  Divider,
  FormControl,
  FormLabel,
  HStack,
  Heading,
  Input,
  Select,
  SkeletonText,
  Stack,
  Text,
  Textarea,
  useToast,
} from "@chakra-ui/react";
import { useMutation, useQuery, useQueryClient } from "react-query";

import { fetchSecret, runInference, type InferencePayload, type InferenceResult } from "../api";

const sessionIdSeed = () => `session-${Date.now()}`;

const policyOptions = [
  { value: "default", label: "Default (mask leaks)" },
  { value: "block-on-leak", label: "Block on leak" },
];

const placeholderPrompt = "Paste or type prompt containing sensitive data...";

const syntheticPreview = (mapping: Record<string, { label: string; synthetic: string }>) =>
  Object.entries(mapping)
    .map(([token, info]) => `${token} → ${info.synthetic}`)
    .join("\n");

export const InferenceConsole = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [inputText, setInputText] = useState<string>("");
  const [sessionId, setSessionId] = useState<string>(sessionIdSeed);
  const [policy, setPolicy] = useState<string>(policyOptions[0].value);
  const [latestSecretId, setLatestSecretId] = useState<string | null>(null);

  const inferenceMutation = useMutation(runInference, {
    onSuccess: (data: InferenceResult) => {
      setLatestSecretId(data.secret_id ?? null);
      if (data.leak_detected) {
        toast({
          title: "Leak detected",
          description: "Response sanitized. Review audit log.",
          status: "warning",
          duration: 6000,
        });
      }
    },
    onError: (error: unknown) => {
      toast({ title: "Request failed", description: String(error), status: "error" });
    },
  });

  const secretQuery = useQuery({
    queryKey: ["secret", latestSecretId],
    queryFn: () => fetchSecret(latestSecretId as string),
    enabled: Boolean(latestSecretId),
    retry: false,
  });

  useEffect(() => {
    if (!inferenceMutation.isLoading) return;
    queryClient.removeQueries({ queryKey: ["secret"] });
  }, [inferenceMutation.isLoading, queryClient]);

  const handleSubmit = () => {
    if (!inputText.trim()) {
      toast({ title: "Prompt required", status: "info" });
      return;
    }
    const payload: InferencePayload = {
      session_id: sessionId,
      input_text: inputText,
      policy,
    };
    inferenceMutation.mutate(payload);
  };

  const mappingPreview = useMemo(() => {
    if (!secretQuery.data) return null;
    return syntheticPreview(secretQuery.data.mapping);
  }, [secretQuery.data]);

  return (
    <Stack spacing={6}>
      <Heading size="lg">Secure Prompt Console</Heading>
      <Stack spacing={4}>
        <HStack spacing={4} align="flex-end">
          <FormControl maxW="xs">
            <FormLabel>Session ID</FormLabel>
            <Input value={sessionId} onChange={(event: ChangeEvent<HTMLInputElement>) => setSessionId(event.target.value)} />
          </FormControl>
          <FormControl maxW="xs">
            <FormLabel>Policy</FormLabel>
            <Select value={policy} onChange={(event: ChangeEvent<HTMLSelectElement>) => setPolicy(event.target.value)}>
              {policyOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          </FormControl>
          <Button variant="ghost" onClick={() => setSessionId(sessionIdSeed())}>
            New session
          </Button>
        </HStack>
        <FormControl>
          <FormLabel>Sensitive prompt</FormLabel>
          <Textarea
            minH="200px"
            value={inputText}
            onChange={(event: ChangeEvent<HTMLTextAreaElement>) => setInputText(event.target.value)}
            placeholder={placeholderPrompt}
          />
        </FormControl>
        <Button
          colorScheme="purple"
          isLoading={inferenceMutation.isLoading}
          onClick={handleSubmit}
          alignSelf="flex-start"
        >
          Send securely
        </Button>
      </Stack>

      <Box borderWidth="1px" borderRadius="lg" p={5} bg="blackAlpha.50" _dark={{ bg: "whiteAlpha.100" }}>
        <Heading size="md" mb={3}>
          Sanitized response
        </Heading>
        {inferenceMutation.data ? (
          <Stack spacing={3}>
            {inferenceMutation.data.leak_detected && (
              <Alert status="warning" borderRadius="md">
                <AlertIcon />
                <AlertDescription>
                  Sensitive content detected in model output. Disclosure prevented.
                </AlertDescription>
              </Alert>
            )}
            <Text whiteSpace="pre-wrap">{inferenceMutation.data.response}</Text>
            <Divider />
            <Text fontSize="sm" color="gray.500">
              Secret ID: {inferenceMutation.data.secret_id ?? "None"}
            </Text>
          </Stack>
        ) : (
          <Text color="gray.500">Run an inference to view sanitized output.</Text>
        )}
      </Box>

      <Box borderWidth="1px" borderRadius="lg" p={5}>
        <Heading size="md" mb={3}>
          Token vault snapshot
        </Heading>
        {secretQuery.isLoading ? (
          <SkeletonText noOfLines={4} />
        ) : secretQuery.data ? (
          <Stack spacing={2}>
            <Text fontSize="sm" color="gray.500">
              Created: {new Date(secretQuery.data.created_at).toLocaleString()}
            </Text>
            <Text fontSize="sm">Detected labels: {(secretQuery.data.detector_metadata.labels as string[] | undefined)?.join(", ") ?? "-"}</Text>
            <Box as="pre" p={3} borderRadius="md" bg="gray.900" color="green.200" fontSize="sm">
              {mappingPreview}
            </Box>
          </Stack>
        ) : (
          <Text color="gray.500">No token mapping retrieved for this session.</Text>
        )}
      </Box>
    </Stack>
  );
};
