r = patch(project_root_path / 'apps/vis-companion/src/components/HumanInputPrompt.tsx', [
 {'from':'2:2c0','to':'12:efd','replace':'''import {
  Banner,
  Button,
  Checkbox,
  ChoiceRow,
  DialogFrame,
  Input,
  Modal,
  ViewHeading,
  ViewLayout,
  ViewParagraph,
} from './ui';'''},
 {'from':'347:091','to':'407:545','replace':'''function HumanInputFieldLabel({ field }: { field: HumanInputField }) {
  return (
    <>
      {field.label}
      {/* The web's own mark, and the TUI band now draws the same one: a red `*`,
          not the word REQUIRED shouted beside every label. Screen readers still
          get the word. */}
      {field.is_required && (
        <>
          <span aria-hidden="true" className="ml-1 text-err">
            *
          </span>
          <span className="sr-only">, required</span>
        </>
      )}
    </>
  );
}

function FieldShell({
  field,
  error,
  controlId,
  labelInControl = false,
  children,
}: {
  field: HumanInputField;
  error?: string;
  /** The native control this visible label names; choice groups name themselves. */
  controlId?: string;
  /** The control already shows the label beside its own mark. */
  labelInControl?: boolean;
  children: React.ReactNode;
}) {
  const labelClass = 'block font-mono text-ui uppercase tracking-[0.08em] text-dialog-hint';
  return (
    <div className="min-w-0 space-y-1">
      {!labelInControl &&
        (controlId ? (
          <label className={labelClass} htmlFor={controlId}>
            <HumanInputFieldLabel field={field} />
          </label>
        ) : (
          <span className={labelClass}>
            <HumanInputFieldLabel field={field} />
          </span>
        ))}
      {field.description && (
        <p
          id={controlId ? `${controlId}-description` : undefined}
          className="font-mono text-ui text-dialog-hint"
        >
          {field.description}
        </p>
      )}
      {children}
      {error && (
        <p id={controlId ? `${controlId}-error` : undefined} className="font-mono text-ui text-err">
          {error}
        </p>
      )}
    </div>
  );
}

/**
 * A field row uses a drawn checkbox for inclusive choices and circular marks for
 * exclusive choices, while keeping the values and validation supplied by the engine.
 */'''},
 {'from':'477:ed7','to':'491:532','replace':'''  if (field.type === 'checkbox') {
    const on = value === true;
    return (
      <FieldShell
        field={field}
        controlId={controlId}
        labelInControl
        {...(error ? { error } : {})}
      >
        <Checkbox
          id={controlId}
          isOn={on}
          disabled={disabled}
          aria-required={field.is_required || undefined}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          onClick={() => onChange(field.id, !on)}
        >
          <HumanInputFieldLabel field={field} />
        </Checkbox>
      </FieldShell>
    );
  }'''},
 {'from':'494:78c','to':'530:c35','replace':'''  if (field.type === 'select' || field.type === 'multiselect') {
    const isMulti = field.type === 'multiselect';
    return (
      <FieldShell field={field} {...(error ? { error } : {})}>
        <div className="space-y-1" role={isMulti ? 'group' : 'radiogroup'} aria-label={field.label}>
          {options.map((option) => {
            const on = isMulti ? chosen.includes(option.value) : value === option.value;
            return isMulti ? (
              <Checkbox
                key={option.value}
                isOn={on}
                disabled={disabled}
                onClick={() =>
                  onChange(field.id, toggleHumanInputOption(field, { [field.id]: chosen }, option.value))
                }
              >
                {option.label}
              </Checkbox>
            ) : (
              <ChoiceRow
                key={option.value}
                isOn={on}
                disabled={disabled}
                role="radio"
                aria-checked={on}
                mark={on ? HUMAN_INPUT_CHOICE_MARKS.exclusiveOn : HUMAN_INPUT_CHOICE_MARKS.exclusiveOff}
                onClick={() => onChange(field.id, option.value)}
              >
                {option.label}
              </ChoiceRow>
            );
          })}
        </div>
      </FieldShell>
    );
  }'}
]); print(r)