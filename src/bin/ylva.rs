use clap::Parser;
use tracing::{debug, info};

use ylva::{
    args::{AssignCommand, Command},
};
use ylva::actions::approve::{approve, ApproveSpec};
use ylva::actions::assign_categories::{assign_categories, AssignCategoriesSpec};
use ylva::actions::assign_payees::{assign_payees, AssignPayeesSpec};
use ylva::args::Args;
use ylva::config::Config;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let subscriber = tracing_subscriber::FmtSubscriber::builder()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    debug!("Parsing command line arguments");
    let args = Args::parse();

    debug!("Loading configuration data");
    let default_config_path = Config::default_path()?;
    let config = if !default_config_path.is_file() {
        Config::create(&default_config_path)?
    } else {
        Config::load(&default_config_path)?
    };

    if args.dry_run {
        info!("Dry-run mode enabled. Not committing any changes");
    }

    match args.command {
        Command::Approve {
            ignore_cleared,
            ignore_category,
            ignore_payee,
        } => {
            approve(&ApproveSpec {
                dry_run: args.dry_run,
                diff: args.diff,
                ignore_cleared,
                ignore_payee,
                ignore_category,
                rate_limit: config.rate_limit,
                api_url: &config.api_url,
                api_token: &config.api_token().await?,
                budget_id: &config.budget_id,
            })
                .await?
        }
        Command::Assign {
            filter,
            force,
            command: AssignCommand::Payees { create_payees },
        } => {
            assign_payees(&AssignPayeesSpec {
                dry_run: args.dry_run,
                diff: args.diff,
                filter,
                force,
                create_payees,
                rate_limit: config.rate_limit,
                api_url: &config.api_url,
                api_token: &config.api_token().await?,
                budget_id: &config.budget_id,
            })
                .await?
        }
        Command::Assign {
            filter,
            force,
            command: AssignCommand::Categories { weekwise },
        } => {
            assign_categories(&AssignCategoriesSpec {
                dry_run: args.dry_run,
                diff: args.diff,
                filter,
                force,
                weekwise,
                rate_limit: config.rate_limit,
                api_url: &config.api_url,
                api_token: &config.api_token().await?,
                budget_id: &config.budget_id,
            })
                .await?
        }
    }

    Ok(())
}
