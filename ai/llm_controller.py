import json
from ollama import chat

from ai.prompt_builder import build_prompt


class LLMController:

    def decide(self, values, previous_setpoint):
        indoor_temp = values["indoor_temp"]

        # -----------------------------------------------------------------
        # HARDCODED SAFETY / PERFORMANCE OVERRIDES (Bypasses LLM when critical)
        # -----------------------------------------------------------------
        # If the building is getting warm, force maximum cooling immediately
        if indoor_temp > 25.0:
            print(f"HYBRID OVERRIDE: Temp ({indoor_temp:.2f}°C) > 25°C. Forcing setpoint to 22.0°C for comfort.")
            return {"setpoint": 22.0}
        
        # If the building is already cool and energy saving is priority, nudge up
        if indoor_temp < 22.5:
            print(f"HYBRID OVERRIDE: Temp ({indoor_temp:.2f}°C) < 22.5°C. Forcing setpoint to 25.5°C to save energy.")
            return {"setpoint": 25.5}

        # -----------------------------------------------------------------
        # LLM DECISION-MAKING (Only used during stable/safe comfort zones)
        # -----------------------------------------------------------------
        prompt = build_prompt(
            values,
            previous_setpoint
        )

        print("Building prompt...")
        print("Calling Ollama...")

        try:
            response = chat(
                model="qwen2.5:3b",
                messages=[
                    {
                        "role": "system",
                        "content": """
                You are an intelligent HVAC controller.

                Your task is to choose ONE cooling setpoint.

                Goals:
                - Reduce HVAC energy aggressively when the room is already cool.
                - Maintain thermal comfort (23°C to 26°C).
                - Avoid unnecessary changes, but INCREASE the setpoint if the room temperature drops below 23°C to save energy.
                - Prefer small adjustments (±1°C) unless a larger correction is needed.
                - Never go below 22°C.
                - Never exceed 26°C.

                Return ONLY JSON.

                Example:

                {
                    "setpoint": 26
                }
                """
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                format="json",
                options={
                    "temperature": 0.1  # Low temperature for strict compliance
                }
            )

            print("Ollama finished.")

            text = response["message"]["content"]

            print("\nLLM RESPONSE")
            print(text)

            decision = json.loads(text)

            setpoint = float(
                decision["setpoint"]
            )

            setpoint = max(
                22.0,
                min(26.0, setpoint)
            )

            return {
                "setpoint": setpoint
            }

        except Exception as e:

            print("Controller Error / Fallback:", e)

            # Keep the previous setpoint if parsing fails
            return {
                "setpoint": previous_setpoint
            }